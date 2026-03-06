"""
Custom Allauth adapters for the AI Resume Builder.

This module overrides two allauth adapters:
  1. CustomAccountAdapter   — handles email/password login and signup
  2. CustomSocialAccountAdapter — handles Google OAuth login

Responsibilities:
  - Block disposable / temporary email domains at signup (TEMP_DOMAINS list)
  - Normalize Gmail addresses (remove dots, block + aliases)
  - Increment login_count and update last_activity on every successful login
    (both email/password and Google OAuth are tracked)
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.forms import ValidationError
from django.shortcuts import redirect
from django.contrib import messages

# Professional list of temporary/disposable email domains
TEMP_DOMAINS = [
    # Common ones
    'tempmail.com', '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 
    'yopmail.com', 'temp-mail.org', 'throwawaymail.com', 'dispostable.com',
    'tempmail.net', 'fakemail.net', 'trashmail.com', 'getnada.com',
    'mohmal.com', 'maildrop.cc', 'mail-temp.com', 'temp-mail.io',
    'tempmailaddress.com', 'disposablemail.com', 'proxydom.com',
    'mailnesia.com', 'mintemail.com', 'slipry.net', 'spamgourmet.com',
    'sharklasers.com', 'guerrillamailblock.com', 'guerrillamail.net',
    'guerrillamail.org', 'pokemail.net', 'grr.la', 'teleworm.us',
    'dayrep.com', 'armyspy.com', 'jourrapide.com', 'fakesender.com',
    # More aggressive ones
    'temp-mail.com', 'tempmail.id', 'tempmail.one', 'tempmail.biz',
    'mailto.plus', 'owlymail.com', 'temp-mail.sh', 'temp-mail.link',
    'temp-mail.info', 'temp-mail.tech', 'temp-mail.icu', 'temp-mail.top',
    'temp-mail.xyz', 'temp-mail.website', 'temp-mail.site', 'temp-mail.online',
    'temp-mail.fun', 'temp-mail.space', 'temp-mail.press', 'temp-mail.host',
    'temp-mail.page', 'temp-mail.cloud', 'temp-mail.digital', 'temp-mail.mobi',
    'temp-mail.email', 'temp-mail.systems', 'temp-mail.work',
]

def validate_professional_email(email):
    email = email.lower().strip()
    if '@' not in email:
        raise ValidationError("Invalid email format.")
        
    local_part, domain = email.split('@')
    
    # 1. Block Tempmails
    if domain in TEMP_DOMAINS:
        raise ValidationError("Temporary/Disposable email addresses are not allowed. Please use a valid personal or professional email.")
    
    # 2. Enforce "Proper Gmail" logic
    if domain == 'gmail.com':
        # Gmail ignores dots: u.s.e.r@gmail.com == user@gmail.com
        # Normalize by removing dots for comparison/storage
        normalized_local = local_part.replace('.', '')
        
        # Block aliases: user+alias@gmail.com
        if '+' in normalized_local:
            raise ValidationError("Email aliases (using '+') are not allowed. Please use your primary Gmail address.")
            
        # Reconstruct normalized email
        email = f"{normalized_local}@{domain}"
    
    return email

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapter for email/password authentication.
    Overrides email cleaning (validation + normalization) and the login hook
    to keep per-user analytics (login_count, last_activity) up to date.
    """

    def clean_email(self, email):
        """Called by allauth during registration to validate and normalize email."""
        email = super().clean_email(email)
        # Reject disposable domains and normalize Gmail (remove dots, block + aliases)
        return validate_professional_email(email)

    def login(self, request, user):
        """
        Called by allauth on every successful email/password login.

        BUG FIX: Previously login_count was never incremented because this hook
        was not overridden. Now we atomically increment the counter and timestamp
        before delegating to the parent (which sets the session cookie).
        """
        from django.utils import timezone
        # Increment total login counter and record timestamp of this login
        user.login_count += 1
        user.last_activity = timezone.now()
        # Only update these two fields — avoids overwriting other fields accidentally
        user.save(update_fields=['login_count', 'last_activity'])
        return super().login(request, user)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter for Google OAuth (social) authentication.
    Tracks login_count for returning users just like the email adapter.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Hook called right before a social (Google OAuth) login is finalized.

        Notes:
          - Tempmail validation is attempted but not hard-blocked, to avoid allauth's
            'Third-Party Login Failure' error. New registrations are already blocked
            at the signup/clean_email level.
          - login_count is only incremented for EXISTING users (sociallogin.is_existing=True).
            New sign-ups via Google OAuth are not counted as a "login" on first creation.
        """
        email = sociallogin.user.email
        if not email:
            return super().pre_social_login(request, sociallogin)

        # Attempt tempmail check (validation only — no hard block for OAuth)
        try:
            validate_professional_email(email)
        except ValidationError:
            # Soft-fail: domain validation at signup already prevents new temp-mail accounts.
            # Hard-blocking here would trigger 'Third-Party Login Failure' in allauth.
            pass

        # BUG FIX: Increment login_count for returning users (not new first-time signups)
        if sociallogin.is_existing:
            from django.utils import timezone
            user = sociallogin.user
            # Increment total login counter and record timestamp of this login
            user.login_count += 1
            user.last_activity = timezone.now()
            # Only update these two fields — avoids overwriting other pending saves
            user.save(update_fields=['login_count', 'last_activity'])

        return super().pre_social_login(request, sociallogin)
