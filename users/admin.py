"""
Full monitoring admin for the AI Resume Builder.
Features: User blocking, API limit control, activity stats, resume tracking.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from django.contrib import messages
from .models import CustomUser, UserProfile, Education, Experience, Skill, Certification, Project


# ─── Inline Admins ──────────────────────────────────────────────────────────

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    fields = ('phone', 'city', 'country', 'job_title', 'linkedin', 'github', 'portfolio', 'summary')
    show_change_link = True


# ─── Admin Actions ───────────────────────────────────────────────────────────

@admin.action(description='🚫 Block selected users (disable AI + login)')
def block_users(modeladmin, request, queryset):
    count = queryset.update(is_blocked=True, is_active=False)
    messages.warning(request, f'{count} user(s) blocked successfully.')


@admin.action(description='✅ Unblock selected users')
def unblock_users(modeladmin, request, queryset):
    count = queryset.update(is_blocked=False, is_active=True)
    messages.success(request, f'{count} user(s) unblocked successfully.')


@admin.action(description='⚡ Set AI limit to 1/day (restrict heavy users)')
def limit_api_1(modeladmin, request, queryset):
    queryset.update(api_daily_limit=1)
    messages.info(request, 'AI daily limit set to 1 for selected users.')


@admin.action(description='⚡ Set AI limit to 3/day')
def limit_api_3(modeladmin, request, queryset):
    queryset.update(api_daily_limit=3)
    messages.info(request, 'AI daily limit set to 3 for selected users.')


@admin.action(description='📄 Set Resume limit to 1/day (default)')
def limit_resume_1(modeladmin, request, queryset):
    queryset.update(resume_daily_limit=1)
    messages.info(request, 'Resume daily limit set to 1 for selected users.')


@admin.action(description='📄 Set Resume limit to 3/day')
def limit_resume_3(modeladmin, request, queryset):
    queryset.update(resume_daily_limit=3)
    messages.info(request, 'Resume daily limit set to 3 for selected users.')


@admin.action(description='📄 Set Resume limit to 5/day')
def limit_resume_5(modeladmin, request, queryset):
    queryset.update(resume_daily_limit=5)
    messages.info(request, 'Resume daily limit set to 5 for selected users.')


@admin.action(description='🔄 Reset Resume limit to system default (2/day)')
def reset_resume_limit(modeladmin, request, queryset):
    queryset.update(resume_daily_limit=0)
    messages.success(request, 'Resume daily limit reset to default (2/day).')


@admin.action(description='⚡ Set AI limit to 10/day (power users)')
def limit_api_10(modeladmin, request, queryset):
    queryset.update(api_daily_limit=10)
    messages.info(request, 'AI daily limit set to 10 for selected users.')


@admin.action(description='🔄 Reset AI limit to system default (5/day)')
def reset_api_limit(modeladmin, request, queryset):
    queryset.update(api_daily_limit=0)
    messages.success(request, 'AI daily limit reset to default (5/day).')


# ─── Main User Admin ─────────────────────────────────────────────────────────

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [UserProfileInline]

    list_display = (
        'email', 'full_name_display', 'status_badge', 'resume_count',
        'ai_calls_today', 'ai_calls_total', 'api_limit_display',
        'resume_limit_display',
        'login_count', 'last_login', 'date_joined',
    )
    list_filter = (
        'is_active', 'is_blocked', 'is_staff',
        'is_profile_complete', 'date_joined',
    )
    search_fields = ('email', 'first_name', 'last_name', 'last_login_ip')
    ordering = ('-date_joined',)
    actions = [block_users, unblock_users,
               limit_api_1, limit_api_3, limit_api_10, reset_api_limit,
               limit_resume_1, limit_resume_3, limit_resume_5, reset_resume_limit]
    readonly_fields = ('date_joined', 'last_login', 'login_count', 'last_login_ip', 'resume_count_readonly', 'ai_usage_summary')
    list_per_page = 30

    fieldsets = (
        ('🔑 Account', {
            'fields': ('email', 'password')
        }),
        ('👤 Personal Info', {
            'fields': ('first_name', 'last_name', 'profile_image')
        }),
        ('🔐 Access Control', {
            'fields': ('is_active', 'is_blocked', 'is_staff', 'is_superuser', 'is_profile_complete'),
            'description': 'Use "is_blocked" to hard-ban a user from the platform. "is_active=False" also disables login.',
        }),
        ('⚡ AI & Resume Limits', {
            'fields': ('api_daily_limit', 'resume_daily_limit'),
            'description': (
                'AI Limit: 0 = system default (5/day). Set custom number to override.\n'
                'Resume Limit: 0 = system default (2/day). Set custom number to override per user.'
            ),
        }),
        ('📊 Activity Stats (Read-only)', {
            'fields': ('date_joined', 'last_login', 'login_count', 'last_login_ip', 'resume_count_readonly', 'ai_usage_summary'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

    # ── Display Helpers ──────────────────────────────────────────────────

    def full_name_display(self, obj):
        name = f'{obj.first_name} {obj.last_name}'.strip()
        return name or '—'
    full_name_display.short_description = 'Name'

    def status_badge(self, obj):
        if obj.is_blocked:
            return format_html('<span style="color:white;background:#dc2626;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">🚫 BLOCKED</span>')
        if obj.is_staff:
            return format_html('<span style="color:white;background:#7c3aed;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">⚙️ STAFF</span>')
        if not obj.is_active:
            return format_html('<span style="color:white;background:#6b7280;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">⛔ INACTIVE</span>')
        return format_html('<span style="color:white;background:#16a34a;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">✅ ACTIVE</span>')
    status_badge.short_description = 'Status'

    def resume_count(self, obj):
        count = obj.resumes.filter(is_active=True).count()
        if count == 0:
            return format_html('<span style="color:#9ca3af">0</span>')
        url = f'/admin/resumes/resume/?user__id__exact={obj.id}'
        return format_html('<a href="{}" style="font-weight:600;color:#6366f1">{} resume{}</a>', url, count, 's' if count != 1 else '')
    resume_count.short_description = '📄 Resumes'

    def ai_calls_today(self, obj):
        from resumes.models import AIPromptLog
        today = timezone.now().date()
        count = AIPromptLog.objects.filter(user=obj, created_at__date=today).count()
        # Get their effective limit
        limit = obj.api_daily_limit if obj.api_daily_limit > 0 else 5
        if count == 0:
            color = '#9ca3af'
        elif count >= limit:
            color = '#dc2626'
        elif count >= limit * 0.7:
            color = '#f59e0b'
        else:
            color = '#16a34a'
        return format_html('<span style="color:{};font-weight:600">{}/{}</span>', color, count, limit)
    ai_calls_today.short_description = '⚡ AI Today'

    def ai_calls_total(self, obj):
        from resumes.models import AIPromptLog
        total = AIPromptLog.objects.filter(user=obj).count()
        return format_html('<span style="font-weight:500">{}</span>', total)
    ai_calls_total.short_description = '📈 AI Total'

    def api_limit_display(self, obj):
        if obj.api_daily_limit == 0:
            return format_html('<span style="color:#9ca3af">Default (5)</span>')
        if obj.api_daily_limit <= 2:
            return format_html('<span style="color:#dc2626;font-weight:600">⚠️ {}/day</span>', obj.api_daily_limit)
        return format_html('<span style="color:#7c3aed;font-weight:600">{}/day</span>', obj.api_daily_limit)
    api_limit_display.short_description = '⚙️ API Limit'

    def resume_count_readonly(self, obj):
        return obj.resumes.filter(is_active=True).count()
    resume_count_readonly.short_description = 'Active Resumes'

    def resume_limit_display(self, obj):
        effective = obj.resume_daily_limit if obj.resume_daily_limit > 0 else 2
        if obj.resume_daily_limit == 0:
            return format_html('<span style="color:#9ca3af">Default (2)</span>')
        if obj.resume_daily_limit == 1:
            return format_html('<span style="color:#f59e0b;font-weight:600">📄 {}/day</span>', obj.resume_daily_limit)
        return format_html('<span style="color:#10b981;font-weight:600">📄 {}/day</span>', obj.resume_daily_limit)
    resume_limit_display.short_description = '📄 Resume Limit'

    def ai_usage_summary(self, obj):
        from resumes.models import AIPromptLog
        today = timezone.now().date()
        logs = AIPromptLog.objects.filter(user=obj)
        total = logs.count()
        today_count = logs.filter(created_at__date=today).count()
        by_type = logs.values('prompt_type').annotate(n=Count('id')).order_by('-n')
        lines = [f'Total AI calls: {total}', f'Today: {today_count}', '---']
        for row in by_type:
            lines.append(f'{row["prompt_type"]}: {row["n"]}')
        return '\n'.join(lines)
    ai_usage_summary.short_description = 'AI Usage Breakdown'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('resumes', 'ai_logs')


# ─── Resume Admin ─────────────────────────────────────────────────────────────

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'profile')
    search_fields = ('institution', 'degree', 'profile__user__email')
    list_filter = ('degree',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'title', 'start_date', 'is_current', 'profile')
    search_fields = ('company', 'title', 'profile__user__email')
    list_filter = ('is_current',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'profile')
    list_filter = ('category', 'proficiency')
    search_fields = ('name',)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'date_obtained', 'profile')
    search_fields = ('name', 'issuer')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'technologies', 'profile')
    search_fields = ('name', 'technologies')
