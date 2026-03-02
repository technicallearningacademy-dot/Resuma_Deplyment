"""
Views for user authentication, registration, and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import CustomUser, UserProfile, Education, Experience, Skill, Certification, Project
from .forms import (
    CustomUserCreationForm, UserProfileForm, ProfileImageForm, CVUploadForm,
    EducationFormSet, ExperienceFormSet, SkillFormSet, CertificationFormSet, ProjectFormSet
)


def landing_page(request):
    """SEO-optimized landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def register_view(request):
    """User registration with email/password."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created! Please complete your profile.')
            return redirect('profile_setup')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Email/password login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_setup(request):
    """Multi-section profile completion after registration."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        education_formset = EducationFormSet(request.POST, instance=profile, prefix='education')
        experience_formset = ExperienceFormSet(request.POST, instance=profile, prefix='experience')
        skill_formset = SkillFormSet(request.POST, instance=profile, prefix='skill')
        certification_formset = CertificationFormSet(request.POST, instance=profile, prefix='certification')
        project_formset = ProjectFormSet(request.POST, instance=profile, prefix='project')

        all_valid = all([
            profile_form.is_valid(),
            image_form.is_valid(),
            education_formset.is_valid(),
            experience_formset.is_valid(),
            skill_formset.is_valid(),
            certification_formset.is_valid(),
            project_formset.is_valid(),
        ])

        if all_valid:
            profile_form.save()
            image_form.save()
            education_formset.save()
            experience_formset.save()
            skill_formset.save()
            certification_formset.save()
            project_formset.save()

            request.user.is_profile_complete = True
            request.user.save()

            messages.success(request, 'Profile saved successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        profile_form = UserProfileForm(instance=profile)
        image_form = ProfileImageForm(instance=request.user)
        education_formset = EducationFormSet(instance=profile, prefix='education')
        experience_formset = ExperienceFormSet(instance=profile, prefix='experience')
        skill_formset = SkillFormSet(instance=profile, prefix='skill')
        certification_formset = CertificationFormSet(instance=profile, prefix='certification')
        project_formset = ProjectFormSet(instance=profile, prefix='project')

    context = {
        'profile_form': profile_form,
        'image_form': image_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
        'skill_formset': skill_formset,
        'certification_formset': certification_formset,
        'project_formset': project_formset,
    }
    return render(request, 'users/profile_setup.html', context)


@login_required
def settings_view(request):
    """User settings page."""
    return render(request, 'users/settings.html')


@login_required
@require_POST
def delete_account(request):
    """Permanently delete user account."""
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been permanently deleted.')
    return redirect('landing')
