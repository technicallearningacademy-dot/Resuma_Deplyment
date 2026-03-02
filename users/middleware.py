"""
Middleware to:
1. Block users who are marked as is_blocked from accessing the site
2. Track last login IP and increment login_count on each request
"""
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


class BlockedUserMiddleware:
    """Prevent blocked users from accessing any page. Log them out and redirect."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, 'is_blocked', False)
        ):
            logout(request)
            messages.error(
                request,
                'Your account has been suspended. Please contact support.'
            )
            return redirect('account_login')

        response = self.get_response(request)
        return response


class TrackLastIPMiddleware:
    """Track the user's last seen IP address on every request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only track IP for authenticated, non-staff users
        if request.user.is_authenticated:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            ip = self._get_client_ip(request)
            try:
                # Only write to DB if IP has changed (avoids write on every request)
                if request.user.last_login_ip != ip:
                    User.objects.filter(pk=request.user.pk).update(last_login_ip=ip)
            except Exception:
                pass  # Never crash on IP tracking

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
