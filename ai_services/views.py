"""
AI service views (AJAX endpoints).
"""
import json
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .client import get_client
from resumes.models import Resume, AIPromptLog

logger = logging.getLogger(__name__)


@login_required
@require_POST
def generate_resume_ai(request):
    """Generate LaTeX resume from user profile data or custom prompt using AI."""
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        template_style = body.get('template_style', 'modern_ats_clean')
        custom_prompt = body.get('custom_prompt', '')
        current_latex = body.get('current_latex', '').strip()
        resume_id = body.get('resume_id')

        client = get_client()

        # Try profile data first; fall back to custom prompt as raw text
        profile_data = _get_profile_data(request.user)

        if current_latex:
            # Re-format existing LaTeX into new template
            combined_prompt = f"Please extract all resume data from this existing LaTeX resume and reformat it flawlessly into the requested template style. Do not lose any information.\n\nEXISTING RESUME LATEX:\n{current_latex}"
            if custom_prompt:
                combined_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_prompt}"
            latex_content = client.generate_from_text(combined_prompt, template_style)
        elif profile_data:
            latex_content = client.generate_latex_resume(profile_data, template_style, custom_prompt)
        elif custom_prompt:
            # No profile but user provided raw text — use it directly
            latex_content = client.generate_from_text(custom_prompt, template_style)
        else:
            return JsonResponse({
                'error': 'Please complete your profile OR paste your resume data in the Custom AI Prompt field.'
            }, status=400)

        if not latex_content:
            return JsonResponse({'error': 'AI returned empty response. Please try again.'}, status=500)

        # Clean the response - remove markdown code fences if present
        latex_content = _clean_latex(latex_content)

        # Save to resume if resume_id provided
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                resume.latex_content = latex_content
                resume.template_name = template_style
                resume.save()
            except Resume.DoesNotExist:
                pass

        # Log the AI interaction
        AIPromptLog.objects.create(
            user=request.user,
            resume_id=resume_id,
            prompt_type='generate',
            prompt=f'Template: {template_style}, Custom: {custom_prompt[:500]}',
            response=latex_content[:2000],
            model_used='gemini-1.5-flash',
        )

        return JsonResponse({'latex': latex_content})

    except Exception as e:
        logger.error(f'AI generation error: {e}')
        return JsonResponse({'error': f'AI error: {str(e)}'}, status=500)


@login_required
@require_POST
def enhance_text_ai(request):
    """Enhance resume text using AI."""
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        text = body.get('text', '')
        context = body.get('context', 'resume')

        if not text:
            return JsonResponse({'error': 'No text provided.'}, status=400)

        client = get_client()
        enhanced = client.enhance_text(text, context)

        if not enhanced:
            return JsonResponse({'error': 'Enhancement failed.'}, status=500)

        return JsonResponse({'enhanced_text': enhanced})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def optimize_keywords_ai(request):
    """Optimize resume keywords for ATS."""
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        resume_text = body.get('resume_text', '')
        job_description = body.get('job_description', '')

        if not resume_text:
            return JsonResponse({'error': 'No resume text provided.'}, status=400)

        client = get_client()
        suggestions = client.optimize_keywords(resume_text, job_description)

        if not suggestions:
            return JsonResponse({'error': 'Optimization failed.'}, status=500)

        return JsonResponse({'suggestions': suggestions})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _get_profile_data(user):
    """Build profile data dict from user's profile."""
    try:
        profile = user.profile
    except Exception:
        return None

    # Check if profile has at least some data
    if not profile.phone and not profile.summary and not profile.job_title:
        return None

    return {
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'email': user.email or '',
        'phone': profile.phone or '',
        'city': profile.city or '',
        'country': profile.country or '',
        'linkedin': profile.linkedin or '',
        'github': profile.github or '',
        'portfolio': profile.portfolio or '',
        'summary': profile.summary or '',
        'job_title': profile.job_title or '',
        'education': list(profile.education_entries.values(
            'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'gpa', 'description'
        )),
        'experience': list(profile.experience_entries.values(
            'company', 'title', 'start_date', 'end_date', 'is_current', 'location', 'description', 'achievements'
        )),
        'skills': list(profile.skills.values('name', 'category', 'proficiency')),
        'certifications': list(profile.certifications.values('name', 'issuer', 'date_obtained', 'credential_url')),
        'projects': list(profile.projects.values('name', 'description', 'technologies', 'url')),
    }


def _clean_latex(text):
    """Remove markdown code fences from AI-generated LaTeX."""
    text = text.strip()
    if text.startswith('```latex'):
        text = text[len('```latex'):].strip()
    elif text.startswith('```'):
        text = text[3:].strip()
    if text.endswith('```'):
        text = text[:-3].strip()
    return text
