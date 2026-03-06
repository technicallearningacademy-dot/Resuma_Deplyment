"""
Middleware to:
1. Block users who are marked as is_blocked from accessing the site
2. Track last login IP and increment login_count on each request
"""
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


class BlockedUserMiddleware:
    """
    Prevent blocked users from accessing any page.
    Log them out immediately and send them to the suspension page.
    Works for BOTH email login AND Google OAuth users.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_staff
            and getattr(request.user, 'is_blocked', False)
        ):
            from django.contrib.auth import logout
            logout(request)
            # Redirect to the professional suspension page (not a generic login page)
            return redirect('account_suspended')

        response = self.get_response(request)
        return response


class TrackLastIPMiddleware:
    """Track the user's last seen IP address and last activity time on every request."""

    ACTIVITY_UPDATE_INTERVAL = 30  # seconds between DB writes

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            from django.utils import timezone
            from django.contrib.auth import get_user_model
            User = get_user_model()
            ip = self._get_client_ip(request)
            now = timezone.now()

            # Throttle: only write to DB at most once every 30 seconds
            last_tracked = request.session.get('_last_activity_tracked', 0)
            if (now.timestamp() - last_tracked) > self.ACTIVITY_UPDATE_INTERVAL:
                update_fields = {}
                if request.user.last_login_ip != ip:
                    update_fields['last_login_ip'] = ip
                update_fields['last_activity'] = now
                try:
                    if update_fields:
                        User.objects.filter(pk=request.user.pk).update(**update_fields)
                except Exception:
                    pass  # Never crash on activity tracking
                request.session['_last_activity_tracked'] = now.timestamp()

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
