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
from allauth.account.models import EmailAddress
from .utils import send_otp_email, send_raw_otp_email
from .models import EmailOTP
import random
import string
import time
from django.utils import timezone


def landing_page(request):
    """SEO-optimized landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def account_suspended(request):
    """Dedicated page shown when a blocked user tries to log in."""
    return render(request, 'users/account_suspended.html')

def register_view(request):
    """User registration with email/password."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            password = request.POST.get('password1')
            
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            request.session['pending_registration'] = {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': password,
            }
            request.session['registration_otp'] = otp_code
            request.session['registration_otp_time'] = timezone.now().timestamp()
            
            if send_raw_otp_email(email, first_name, otp_code):
                messages.success(request, 'Please check your email for the verification code to complete your registration.')
                return redirect('verify_email_otp')
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
                return redirect('register')
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
            # Check if user is blocked
            if user.is_blocked:
                return redirect('account_suspended')
            
            # Check if email is verified
            email_address = EmailAddress.objects.filter(user=user, email=email).first()
            if email_address and not email_address.verified:
                send_otp_email(user)
                request.session['verification_user_id'] = user.id
                messages.error(request, 'Please verify your email address to sign in. A new 6-digit code has been sent to your inbox.')
                return redirect('verify_email_otp')

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Track login stats
            user.login_count += 1
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                user.last_login_ip = x_forwarded_for.split(',')[0].strip()
            else:
                user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save(update_fields=['login_count', 'last_login_ip'])
            
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please check your credentials and try again.')
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

    just_verified = request.session.pop('just_verified', False)

    context = {
        'profile_form': profile_form,
        'image_form': image_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
        'skill_formset': skill_formset,
        'certification_formset': certification_formset,
        'project_formset': project_formset,
        'just_verified': just_verified,
    }
    return render(request, 'users/profile_setup.html', context)


@login_required
def settings_view(request):
    """User settings page."""
    try:
        profile = request.user.profile
    except Exception:
        profile = None

    if request.method == 'POST' and 'update_theme' in request.POST:
        if profile:
            new_theme = request.POST.get('app_theme')
            if new_theme in dict(UserProfile.THEME_CHOICES):
                # Check SiteConfiguration to make sure it's enabled
                from site_config.models import SiteConfiguration
                config = SiteConfiguration.load()
                
                if new_theme == UserProfile.THEME_PINK_3D and not config.enable_pink_theme:
                    messages.error(request, 'Pink Horizon theme is currently disabled by administrators.')
                elif new_theme == UserProfile.THEME_VIOLET_3D and not config.enable_violet_theme:
                    messages.error(request, 'Deep Violet X theme is currently disabled by administrators.')
                else:
                    profile.app_theme = new_theme
                    profile.save()
                    messages.success(request, 'Theme updated successfully!')
        else:
            messages.error(request, 'Please complete your profile setup first.')
            
        return redirect('settings')

    # Load config to pass to template so we can hide disabled themes
    from site_config.models import SiteConfiguration
    config = SiteConfiguration.load()

    context = {
        'profile': profile,
        'config': config
    }
    return render(request, 'users/settings.html', context)


@login_required
@require_POST
def delete_account(request):
    """Permanently delete user account."""
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been permanently deleted.')
    return redirect('landing')

def verify_email_otp(request):
    """View to handle submitting the 6-digit OTP."""
    user_id = request.session.get('verification_user_id')
    pending_reg = request.session.get('pending_registration')
    
    if not user_id and not pending_reg:
        messages.error(request, 'Verification session expired. Please log in or register again.')
        return redirect('login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        
        if pending_reg:
            expected_otp = request.session.get('registration_otp')
            otp_time = request.session.get('registration_otp_time', 0)
            
            if time.time() - otp_time > 900:  # 15 mins
                messages.error(request, 'Verification code expired. Please request a new one.')
            elif otp_input == expected_otp:
                # Actually create the user in DB now
                user = CustomUser.objects.create_user(
                    email=pending_reg['email'],
                    password=pending_reg['password'],
                    first_name=pending_reg['first_name'],
                    last_name=pending_reg['last_name']
                )
                EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
                
                # Clean up session
                del request.session['pending_registration']
                del request.session['registration_otp']
                del request.session['registration_otp_time']
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['just_verified'] = True
                messages.success(request, "Account created and verified successfully! Let's set up your profile.")
                return redirect('profile_setup')
            else:
                messages.error(request, 'Invalid verification code.')
                
        elif user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            valid_otp = EmailOTP.objects.filter(user=user, code=otp_input, is_used=False).first()
            
            if valid_otp and valid_otp.is_valid():
                valid_otp.is_used = True
                valid_otp.save()
                EmailAddress.objects.filter(user=user).update(verified=True)
                del request.session['verification_user_id']
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Email verified successfully! Welcome.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid or expired verification code.')
            
    # Determine which email to show on the UI
    display_email = pending_reg['email'] if pending_reg else CustomUser.objects.get(id=user_id).email
            
    return render(request, 'users/verify_otp.html', {'email_to_verify': display_email})

@require_POST
def resend_otp(request):
    """View to resend OTP email."""
    user_id = request.session.get('verification_user_id')
    pending_reg = request.session.get('pending_registration')
    
    if not user_id and not pending_reg:
        messages.error(request, 'Verification session expired. Please log in or register again.')
        return redirect('login')
        
    if pending_reg:
        otp_code = ''.join(random.choices(string.digits, k=6))
        request.session['registration_otp'] = otp_code
        request.session['registration_otp_time'] = timezone.now().timestamp()
        
        if send_raw_otp_email(pending_reg['email'], pending_reg['first_name'], otp_code):
            messages.success(request, 'A new verification code has been sent to your email.')
        else:
            messages.error(request, 'Failed to send verification code. Please try again later.')
            
    elif user_id:
        user = get_object_or_404(CustomUser, id=user_id)
        if send_otp_email(user):
            messages.success(request, 'A new verification code has been sent to your email.')
        else:
            messages.error(request, 'Failed to send verification code. Please try again later.')
        
    return redirect('verify_email_otp')


@login_required
@require_POST
def upload_photo_ajax(request):
    """AJAX endpoint for uploading profile picture from Builder."""
    if 'profile_image' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No image provided.'}, status=400)
    
    user = request.user
    user.profile_image = request.FILES['profile_image']
    user.save()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Image uploaded successfully.',
        'url': user.profile_image.url
    })
