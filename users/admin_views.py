"""
Real-time admin monitoring dashboard views.
Access at: /admin-monitor/       — HTML dashboard
Access at: /admin-monitor/api/   — JSON data for auto-refresh
Access at: /admin-monitor/set-limits/  — POST to update per-user limits
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json


def _get_stats():
    """Compute all live stats for the admin dashboard."""
    from users.models import CustomUser
    from resumes.models import Resume
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    online_threshold = now - timedelta(minutes=5)

    # --- User Stats ---
    all_users = CustomUser.objects.all()
    total_users = all_users.count()
    online_users = all_users.filter(last_activity__gte=online_threshold, is_blocked=False).count()
    blocked_users = all_users.filter(is_blocked=True).count()
    new_today = all_users.filter(date_joined__gte=today_start).count()

    # --- Resume Stats ---
    resumes_today = Resume.objects.filter(created_at__gte=today_start, is_active=True).count()
    total_resumes = Resume.objects.filter(is_active=True).count()

    # --- AI Stats ---
    ai_today = 0
    ai_total = 0
    recent_ai_logs = []
    try:
        from resumes.models import AIPromptLog
        ai_today = AIPromptLog.objects.filter(created_at__gte=today_start).count()
        ai_total = AIPromptLog.objects.count()
        recent_ai_logs = list(
            AIPromptLog.objects.select_related('user')
            .order_by('-created_at')[:15]
            .values('user__email', 'prompt_type', 'created_at', 'model_used')
        )
        for log in recent_ai_logs:
            log['created_at'] = log['created_at'].strftime('%b %d, %H:%M')
    except Exception:
        pass

    # --- Live User Activity Table ---
    users_data = []
    for u in all_users.order_by('-last_activity')[:50]:
        is_online = (
            u.last_activity is not None
            and u.last_activity >= online_threshold
            and not u.is_blocked
        )
        last_seen = 'Never'
        if u.last_activity:
            delta = now - u.last_activity
            if delta.total_seconds() < 60:
                last_seen = 'Just now'
            elif delta.total_seconds() < 3600:
                mins = int(delta.total_seconds() // 60)
                last_seen = f'{mins}m ago'
            elif delta.days == 0:
                hrs = int(delta.total_seconds() // 3600)
                last_seen = f'{hrs}h ago'
            else:
                last_seen = u.last_activity.strftime('%b %d, %H:%M')

        resumes_created = Resume.objects.filter(user=u, is_active=True).count()
        ai_used_today = u.resumes_created_today if u.last_resume_creation_date == now.date() else 0

        users_data.append({
            'id': u.pk,
            'email': u.email,
            'name': u.full_name or u.email,
            'is_online': is_online,
            'is_blocked': u.is_blocked,
            'last_seen': last_seen,
            'last_ip': u.last_login_ip or '—',
            'login_count': u.login_count,
            'resumes': resumes_created,
            'ai_today': ai_used_today,
            'joined': u.date_joined.strftime('%b %d, %Y'),
            # Limits
            'ai_limit': u.api_daily_limit,        # 0 = default (5)
            'resume_limit': u.resume_daily_limit,  # 0 = default (1)
            'ai_limit_effective': u.get_ai_daily_limit(),
            'resume_limit_effective': u.get_resume_daily_limit(),
        })

    return {
        'total_users': total_users,
        'online_users': online_users,
        'blocked_users': blocked_users,
        'new_today': new_today,
        'resumes_today': resumes_today,
        'total_resumes': total_resumes,
        'ai_today': ai_today,
        'ai_total': ai_total,
        'users_data': users_data,
        'recent_ai_logs': recent_ai_logs,
        'last_updated': now.strftime('%H:%M:%S'),
    }


@staff_member_required
def admin_monitor(request):
    """Render the real-time admin monitoring dashboard."""
    stats = _get_stats()
    return render(request, 'admin/admin_monitor.html', stats)


@staff_member_required
def admin_monitor_api(request):
    """JSON endpoint polled by the dashboard every 10 seconds."""
    stats = _get_stats()
    return JsonResponse(stats)


@staff_member_required
@require_POST
def update_user_limits(request):
    """
    AJAX endpoint to update a user's AI and resume daily limits.
    Called by the dashboard's inline limit editors.
    POST body (JSON): { user_id, ai_limit, resume_limit }
    """
    from users.models import CustomUser
    try:
        data = json.loads(request.body)
        user_id = int(data.get('user_id', 0))
        ai_limit = int(data.get('ai_limit', 0))
        resume_limit = int(data.get('resume_limit', 0))

        if user_id <= 0:
            return JsonResponse({'ok': False, 'error': 'Invalid user_id'}, status=400)
        if ai_limit < 0 or resume_limit < 0:
            return JsonResponse({'ok': False, 'error': 'Limits cannot be negative'}, status=400)

        updated = CustomUser.objects.filter(pk=user_id).update(
            api_daily_limit=ai_limit,
            resume_daily_limit=resume_limit,
        )
        if not updated:
            return JsonResponse({'ok': False, 'error': 'User not found'}, status=404)

        user = CustomUser.objects.get(pk=user_id)
        return JsonResponse({
            'ok': True,
            'ai_limit_effective': user.get_ai_daily_limit(),
            'resume_limit_effective': user.get_resume_daily_limit(),
        })
    except (ValueError, json.JSONDecodeError) as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': 'Server error'}, status=500)
