"""
Views for resume CRUD, builder, history, and downloads.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils import timezone
from .models import Resume, ResumeVersion, UploadedCV


@login_required
def dashboard(request):
    """Main dashboard showing user's resumes."""
    resumes = Resume.objects.filter(user=request.user, is_active=True)
    
    # Check if user can create a new resume today using User model tracker
    can_create_resume = request.user.can_create_resume_today()
    
    return render(request, 'resumes/dashboard.html', {
        'resumes': resumes,
        'can_create_resume': can_create_resume
    })


@login_required
def create_resume(request):
    """Create a new resume (limited to 1 per day per user)."""
    # Restrict using the User model persistent tracker
    if not request.user.can_create_resume_today():
        messages.error(request, 'You have reached your limit of creating 1 resume per day. Please try again tomorrow.')
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Resume')
        template = request.POST.get('template', 'modern_ats_clean')
        resume = Resume.objects.create(
            user=request.user,
            title=title,
            template_name=template,
        )
        
        # Record the creation so limits persist even if deleted
        request.user.increment_resume_creation()
        
        messages.success(request, f'Resume "{title}" created!')
        return redirect('resume_builder', resume_id=resume.id)
    return render(request, 'resumes/create.html')


@login_required
def resume_builder(request, resume_id):
    """Split-screen resume builder with editor and preview."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "The resume you are looking for does not exist or you do not have permission to access it.")
        return redirect('dashboard')
    
    versions = resume.versions.all()[:10]

    # Get user profile data for template filling
    profile_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        profile_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'city': profile.city,
            'country': profile.country,
            'linkedin': profile.linkedin,
            'github': profile.github,
            'portfolio': profile.portfolio,
            'summary': profile.summary,
            'job_title': profile.job_title,
            'education': list(profile.education_entries.values()),
            'experience': list(profile.experience_entries.values()),
            'skills': list(profile.skills.values()),
            'certifications': list(profile.certifications.values()),
            'projects': list(profile.projects.values()),
        }

    template_choices = Resume.TEMPLATE_CHOICES

    context = {
        'resume': resume,
        'versions': versions,
        'profile_data': json.dumps(profile_data, default=str),
        'template_choices': template_choices,
    }
    return render(request, 'resumes/builder.html', context)


@login_required
@require_POST
def save_resume(request, resume_id):
    """Save resume content and create version."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Resume not found.'}, status=404)

    latex_content = request.POST.get('latex_content', '')
    template_name = request.POST.get('template_name', resume.template_name)
    change_note = request.POST.get('change_note', '')

    resume.latex_content = latex_content
    resume.template_name = template_name
    resume.save()

    # Create version
    last_version = resume.versions.first()
    version_number = (last_version.version_number + 1) if last_version else 1

    ResumeVersion.objects.create(
        resume=resume,
        version_number=version_number,
        latex_content=latex_content,
        change_note=change_note,
    )

    return JsonResponse({'status': 'success', 'version': version_number})


@login_required
def resume_history(request, resume_id):
    """View version history for a resume."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "The resume you are looking for does not exist or you do not have permission to access it.")
        return redirect('dashboard')
    versions = resume.versions.all()
    return render(request, 'resumes/history.html', {'resume': resume, 'versions': versions})


@login_required
@require_POST
def rollback_version(request, resume_id, version_id):
    """Rollback to a previous version."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        version = ResumeVersion.objects.get(id=version_id, resume=resume)
    except (Resume.DoesNotExist, ResumeVersion.DoesNotExist):
        messages.error(request, "The resume or version you are looking for does not exist.")
        return redirect('dashboard')

    resume.latex_content = version.latex_content
    resume.save()

    messages.success(request, f'Rolled back to version {version.version_number}')
    return redirect('resume_builder', resume_id=resume.id)


@login_required
@require_POST
def duplicate_resume(request, resume_id):
    """Duplicate a resume (limited to 1 per day per user)."""
    if not request.user.can_create_resume_today():
        messages.error(request, 'You have reached your limit of creating/duplicating 1 resume per day. Please try again tomorrow.')
        return redirect('dashboard')

    try:
        original = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "The resume you are trying to duplicate does not exist.")
        return redirect('dashboard')
    new_resume = Resume.objects.create(
        user=request.user,
        title=f'{original.title} (Copy)',
        template_name=original.template_name,
        latex_content=original.latex_content,
    )
    
    # Record the creation so limits persist even if deleted
    request.user.increment_resume_creation()
    
    messages.success(request, f'Resume duplicated as "{new_resume.title}"')
    return redirect('resume_builder', resume_id=new_resume.id)


@login_required
@require_POST
def delete_resume(request, resume_id):
    """Delete a resume permanently."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "The resume you are trying to delete does not exist.")
        return redirect('dashboard')
    resume.delete()
    messages.success(request, 'Resume deleted.')
    return redirect('dashboard')


@login_required
@xframe_options_exempt
def preview_resume_pdf(request, resume_id):
    """Generate and return a PDF for live preview without saving."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        return HttpResponse("Resume not found.", status=404)
    
    latex_content = ''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latex_content = data.get('latex_content', '')
        except json.JSONDecodeError:
            latex_content = request.POST.get('latex_content', '')

    if not latex_content:
        latex_content = resume.latex_content

    from templates_engine.compiler import compile_latex_to_pdf
    
    try:
        pdf_content = compile_latex_to_pdf(latex_content)
        
        if pdf_content:
            return HttpResponse(pdf_content, content_type='application/pdf')
        else:
            return JsonResponse({'error': 'Failed to generate PDF preview (no content)'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def download_resume(request, resume_id, file_format):
    """Download resume as PDF or DOCX."""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "The resume you are trying to download does not exist.")
        return redirect('dashboard')

    if file_format == 'pdf':
        # Generate PDF from LaTeX
        from templates_engine.compiler import compile_latex_to_pdf
        pdf_content = compile_latex_to_pdf(resume.latex_content)
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
            return response
        else:
            messages.error(request, 'Failed to generate PDF. Please check your LaTeX code.')
            return redirect('resume_builder', resume_id=resume.id)

    elif file_format == 'docx':
        from templates_engine.converter import latex_to_docx
        docx_content = latex_to_docx(resume.latex_content, resume.title)
        if docx_content:
            response = HttpResponse(
                docx_content,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{resume.title}.docx"'
            return response
        else:
            messages.error(request, 'Failed to generate DOCX.')
            return redirect('resume_builder', resume_id=resume.id)

    messages.error(request, 'Invalid format.')
    return redirect('resume_builder', resume_id=resume.id)

def public_resume_view(request, token):
    """
    Public, read-only view of a resume using its secure sharing token.
    Allows anyone with the link to view the PDF.
    """
    resume = get_object_or_404(Resume, share_token=token, is_active=True, is_public=True)
    return render(request, 'resumes/public_view.html', {'resume': resume})


@xframe_options_exempt
def public_preview_resume_pdf(request, token):
    """
    Generate and return a PDF for the public share page iframe without requiring login.
    """
    resume = get_object_or_404(Resume, share_token=token, is_active=True, is_public=True)
    
    from templates_engine.compiler import compile_latex_to_pdf
    
    try:
        pdf_content = compile_latex_to_pdf(resume.latex_content)
        if pdf_content:
            return HttpResponse(pdf_content, content_type='application/pdf')
        else:
            return HttpResponse("Failed to generate PDF.", status=400)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


def public_download_resume(request, token):
    """
    Download a PDF of the resume from the public share link without requiring login.
    """
    resume = get_object_or_404(Resume, share_token=token, is_active=True, is_public=True)
    
    from templates_engine.compiler import compile_latex_to_pdf
    pdf_content = compile_latex_to_pdf(resume.latex_content)
    
    if pdf_content:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
        return response
    else:
        return HttpResponse("Failed to generate PDF for download.", status=500)
