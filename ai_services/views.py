"""
AI service views (AJAX endpoints).

These views power the AI features in the resume builder. All endpoints are:
  - Login-required (no anonymous AI access)
  - POST-only (stateful AI operations)
  - Rate-limited per user per day (enforced via rate_limiter.py)

Rate-limiting Architecture:
  Each user has an admin-configurable daily limit stored on CustomUser.api_daily_limit.
  The check_rate_limit() helper counts today's AIPromptLog entries for the user and
  compares against their effective limit (per-user override, or system default).
  If the limit is exceeded, a 429 JSON response is returned BEFORE any AI call is made,
  meaning the AI API is never hit and the user is not charged.

  Default daily limits (overridable per user by admin):
    - generate  →  5 / day   (most expensive — full resume generation)
    - enhance   →  10 / day  (cheap — single text block enhancement)
    - optimize  →  3 / day   (keyword analysis against job description)
    - extract   →  2 / day   (CV data extraction from uploaded file)
"""
import json
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .client import get_client
from .rate_limiter import check_rate_limit, rate_limit_response  # Per-user daily rate limiter
from resumes.models import Resume, AIPromptLog, ResumeChatMessage

logger = logging.getLogger(__name__)


@login_required
@require_POST
def generate_resume_ai(request):
    """
    Generate a full LaTeX resume from the user's profile data using AI.

    Supports three modes depending on what context is provided:
      1. Chat edit  — resume_id + current_latex + custom_prompt  → conversational edit via chat history
      2. Reformat   — current_latex only                         → reformat existing LaTeX into a new template
      3. First gen  — profile_data (or raw custom_prompt)        → first-time generation from user profile

    Rate limit: 'generate' action (5/day default, admin-adjustable per user).
    Returns JSON: { latex: <string> } on success, or { error, rate_limited } on failure.
    """
    # ── Enforce per-user daily rate limit BEFORE hitting the AI API ───────────
    # check_rate_limit() reads today's AIPromptLog count for this user and action.
    # If the user has exhausted their quota, we return a 429 immediately — no AI call is made.
    allowed, used, limit = check_rate_limit(request.user, 'generate')
    if not allowed:
        return rate_limit_response('generate', used, limit)
    # ─────────────────────────────────────────────────────────────────────────
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        template_style = body.get('template_style', 'modern_ats_clean')
        custom_prompt = body.get('custom_prompt', '')
        current_latex = body.get('current_latex', '').strip()
        resume_id = body.get('resume_id')

        client = get_client()

        # Try profile data first; fall back to custom prompt as raw text
        profile_data = _get_profile_data(request.user)
        resume = None
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
            except Resume.DoesNotExist:
                pass

        if resume and current_latex and custom_prompt:
            # We are in an active edit session with a custom prompt
            # Save the user's new prompt to history
            ResumeChatMessage.objects.create(resume=resume, role='user', content=custom_prompt)
            
            # Fetch history
            chat_history = resume.chat_messages.all()
            
            # Use the new chat interface
            latex_content = client.chat_resume_edit(
                user_prompt=custom_prompt,
                profile_data=profile_data,
                current_latex=current_latex,
                template_style=template_style,
                chat_history_qs=chat_history
            )
            
            # Save the AI's response to history
            if latex_content:
                ResumeChatMessage.objects.create(resume=resume, role='model', content=latex_content)
                
        elif current_latex:
            # Re-format existing LaTeX into new template (no custom prompt)
            combined_prompt = f"Please extract all resume data from this existing LaTeX resume and reformat it flawlessly into the requested template style. Do not lose any information.\n\nEXISTING RESUME LATEX:\n{current_latex}"
            latex_content = client.generate_from_text(combined_prompt, template_style)
        elif profile_data:
            # First time generation from profile
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
        if resume:
            resume.latex_content = latex_content
            resume.template_name = template_style
            resume.save()

        # Log the AI interaction
        AIPromptLog.objects.create(
            user=request.user,
            resume_id=resume_id,
            prompt_type='generate',
            prompt=f'Template: {template_style}, Custom: {custom_prompt[:500]}',
            response=latex_content[:2000],
            model_used='gemini-2.0-flash-lite',
        )

        return JsonResponse({'latex': latex_content})

    except Exception as e:
        logger.error(f'AI generation error: {e}')
        return JsonResponse({'error': f'AI error: {str(e)}'}, status=500)


@login_required
@require_POST
def enhance_text_ai(request):
    """
    Enhance a selected block of resume text using AI.

    Accepts a text snippet (e.g., a bullet point or summary paragraph) and an optional
    context string describing where the text lives (e.g., 'resume bullet point').
    Returns an improved version of the text with better grammar, impact, and phrasing.

    Rate limit: 'enhance' action (10/day default).
    Returns JSON: { enhanced_text: <string> } on success.
    """
    # ── Enforce per-user daily rate limit BEFORE hitting the AI API ───────────
    allowed, used, limit = check_rate_limit(request.user, 'enhance')
    if not allowed:
        return rate_limit_response('enhance', used, limit)
    # ─────────────────────────────────────────────────────────────────────────
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
    """
    Analyze the resume for ATS keyword gaps against a provided job description.

    Accepts the full resume LaTeX text and an optional job description string.
    Returns AI-generated keyword suggestions and recommendations to improve ATS pass-through.

    Rate limit: 'optimize' action (3/day default — heavier prompt).
    Returns JSON: { suggestions: <string> } on success.
    """
    # ── Enforce per-user daily rate limit BEFORE hitting the AI API ───────────
    allowed, used, limit = check_rate_limit(request.user, 'optimize')
    if not allowed:
        return rate_limit_response('optimize', used, limit)
    # ─────────────────────────────────────────────────────────────────────────
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

@login_required
def fetch_chat_history(request, resume_id):
    """Fetch the AI chat history for a specific resume."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        messages = resume.chat_messages.all()
        
        history = [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return JsonResponse({'history': history})
        
    except Resume.DoesNotExist:
        return JsonResponse({'error': 'Resume not found.'}, status=404)
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


@login_required
@require_POST
def chat_with_ai(request):
    """
    Conversational AI endpoint — returns plain-text advice about resume topics.
    Does NOT generate or modify LaTeX. Used for the 'Ask AI' chat mode.

    Rate limit: uses 'enhance' bucket (10/day default).
    Returns JSON: { reply: <string>, role: 'model' }
    """
    # ── Enforce per-user daily rate limit ────────────────────────────────────
    allowed, used, limit = check_rate_limit(request.user, 'enhance')
    if not allowed:
        return rate_limit_response('enhance', used, limit)
    # ─────────────────────────────────────────────────────────────────────────
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        message = body.get('message', '').strip()
        resume_id = body.get('resume_id')

        if not message:
            return JsonResponse({'error': 'No message provided.'}, status=400)

        # Load chat history for multi-turn context (last 10 messages)
        chat_history = None
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                chat_history = resume.chat_messages.all().order_by('created_at')[:20]
                # Save the user message
                ResumeChatMessage.objects.create(resume=resume, role='user', content=message)
            except Resume.DoesNotExist:
                pass

        client = get_client()
        reply = client.chat_with_assistant(message, chat_history)

        if not reply:
            return JsonResponse({'error': 'AI returned empty response. Please try again.'}, status=500)

        # Save AI reply to chat history
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                ResumeChatMessage.objects.create(resume=resume, role='model', content=reply)
            except Resume.DoesNotExist:
                pass

        # Log the interaction
        AIPromptLog.objects.create(
            user=request.user,
            prompt_type='enhance',
            prompt=message[:500],
            response=reply[:2000],
            model_used='gemini-2.0-flash-lite',
        )

        return JsonResponse({'reply': reply, 'role': 'model'})

    except Exception as e:
        logger.error(f'Chat error: {e}')
        return JsonResponse({'error': f'AI error: {str(e)}'}, status=500)


@login_required
@require_POST
def extract_pdf_ai(request):
    """
    PDF upload and extraction endpoint.
    Accepts a PDF file, extracts its text with PyMuPDF, and sends it to AI
    for structured resume data extraction.

    Rate limit: 'extract' action (2/day default).
    Returns JSON: { extracted_data: <dict>, raw_text: <string> }
    """
    # ── Enforce per-user daily rate limit ────────────────────────────────────
    allowed, used, limit = check_rate_limit(request.user, 'extract')
    if not allowed:
        return rate_limit_response('extract', used, limit)
    # ─────────────────────────────────────────────────────────────────────────
    try:
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return JsonResponse({'error': 'No PDF file uploaded.'}, status=400)

        # Validate file type
        if not pdf_file.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files are accepted.'}, status=400)

        # Limit to 10MB
        if pdf_file.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File too large. Max 10MB.'}, status=400)

        # Extract text using PyMuPDF
        import fitz  # PyMuPDF
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
        raw_text = ''
        for page in doc:
            raw_text += page.get_text()
        doc.close()

        if not raw_text.strip():
            return JsonResponse({'error': 'Could not extract text from this PDF. It may be scanned/image-only.'}, status=400)

        # Truncate to 8000 chars to stay within token limits
        raw_text_trimmed = raw_text[:8000]

        # Send to AI for structured extraction
        client = get_client()
        extracted_json_str = client.extract_from_pdf(raw_text_trimmed)

        # Parse JSON response
        import re as _re
        json_match = _re.search(r'\{[\s\S]*\}', extracted_json_str)
        if json_match:
            import json as _json
            extracted_data = _json.loads(json_match.group())
        else:
            extracted_data = {}

        # Log the extraction
        AIPromptLog.objects.create(
            user=request.user,
            prompt_type='extract',
            prompt=f'PDF: {pdf_file.name} ({len(raw_text)} chars extracted)',
            response=extracted_json_str[:2000],
            model_used='gemini-2.0-flash-lite',
        )

        return JsonResponse({
            'extracted_data': extracted_data,
            'raw_text': raw_text_trimmed,
            'filename': pdf_file.name,
        })

    except Exception as e:
        logger.error(f'PDF extraction error: {e}')
        return JsonResponse({'error': f'Extraction failed: {str(e)}'}, status=500)

