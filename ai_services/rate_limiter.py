"""
Per-user daily AI usage rate limiter.
Uses the existing AIPromptLog model to count today's requests per user.

Daily Limits Per User (system defaults):
  - generate:  5 / day  (can be overridden per user via admin api_daily_limit field)
  - enhance:   10 / day
  - optimize:  3 / day
  - extract:   2 / day
"""
from django.utils import timezone
from django.http import JsonResponse


# System-wide default daily limits per action type
DAILY_LIMITS = {
    'generate': 50,    # Resume generation (most expensive)
    'enhance': 10,    # Text enhancement (cheap)
    'optimize': 3,    # Keyword optimization
    'extract': 20,    # CV data extraction
}

# Human-readable names for error messages
ACTION_NAMES = {
    'generate': 'resume generations',
    'enhance': 'text enhancements',
    'optimize': 'keyword optimizations',
    'extract': 'CV extractions',
}


def _get_limit_for_user(user, action_type):
    """
    Get the effective daily limit for a user and action.
    Respects the admin-set api_daily_limit override for 'generate' actions.
    """
    default = DAILY_LIMITS.get(action_type, 5)
    if action_type == 'generate':
        # Admin can set a custom per-user limit (0 = use default)
        custom = getattr(user, 'api_daily_limit', 0)
        return custom if custom > 0 else default
    return default


def get_usage_today(user, action_type):
    """Count how many times the user has used this action today."""
    from resumes.models import AIPromptLog
    today = timezone.now().date()
    return AIPromptLog.objects.filter(
        user=user,
        prompt_type=action_type,
        created_at__date=today,
    ).count()


def check_rate_limit(user, action_type):
    """
    Check if the user has exceeded their daily limit for the given action.
    Returns (allowed: bool, used: int, limit: int).
    """
    limit = _get_limit_for_user(user, action_type)
    used = get_usage_today(user, action_type)
    allowed = used < limit
    return allowed, used, limit


def rate_limit_response(action_type, used, limit):
    """Return a user-friendly JSON error response when the limit is exceeded."""
    name = ACTION_NAMES.get(action_type, action_type)
    return JsonResponse({
        'error': (
            f"You have reached your daily limit of {limit} {name}. "
            f"Your quota will automatically reset at midnight. Please try again tomorrow or contact support to upgrade your limits."
        ),
        'rate_limited': True,
        'used': used,
        'limit': limit,
        'action': action_type,
    }, status=429)


def get_usage_summary(user):
    """Return a full usage summary for all action types for today."""
    summary = {}
    for action_type in DAILY_LIMITS:
        limit = _get_limit_for_user(user, action_type)
        used = get_usage_today(user, action_type)
        summary[action_type] = {
            'used': used,
            'limit': limit,
            'remaining': max(0, limit - used),
            'name': ACTION_NAMES[action_type],
        }
    return summary
