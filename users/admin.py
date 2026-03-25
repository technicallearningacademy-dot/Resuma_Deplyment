"""
Full monitoring admin for the AI Resume Builder.
Features: User blocking, API limit control, activity stats, resume tracking.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.timezone import now
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
import json
from django.contrib import messages
from .models import CustomUser, UserProfile, Education, Experience, Skill, Certification, Project
from allauth.account.models import EmailAddress
from django.db.models import Count


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
        'avatar_thumbnail', 'email', 'full_name_display', 'status_badge', 
        'location_badge', 'email_verified_badge', 'resume_count',
        'ai_calls_today', 'ai_calls_total', 'last_seen_delta', 'date_joined',
    )
    list_display_links = ('avatar_thumbnail', 'email')
    list_filter = (
        'is_active', 'is_blocked', 'is_staff',
        'is_profile_complete', 'date_joined',
    )
    search_fields = (
        'email', 'first_name', 'last_name', 'last_login_ip',
        'profile__city', 'profile__country', 'profile__job_title'
    )
    ordering = ('-date_joined',)
    actions = [block_users, unblock_users,
               limit_api_1, limit_api_3, limit_api_10, reset_api_limit,
               limit_resume_1, limit_resume_3, limit_resume_5, reset_resume_limit]
    readonly_fields = ('date_joined', 'last_login', 'login_count', 'last_login_ip', 'resume_count_readonly', 'ai_usage_summary', 'ai_calls_today', 'stats_visual', 'profile_quick_links')
    list_per_page = 30

    fieldsets = (
        ('🔑 Account & Password', {
            'fields': ('email', 'password'),
            'classes': ('collapse',),
        }),
        ('👤 Personal Identity', {
            'fields': ('first_name', 'last_name', 'profile_image')
        }),
        ('📊 User Performance & Usage Statistics', {
            'fields': ('stats_visual',),
            'description': 'A real-time overview of this user’s activity and platform success.'
        }),
        ('🛡️ User Support & Restriction Dashboard', {
            'fields': (
                'is_active', 'is_blocked', 'is_staff', 'is_profile_complete',
                'api_daily_limit', 'ai_calls_today',
                'resume_daily_limit', 'resumes_created_today'
            ),
            'description': format_html(
                '<div style="background:#fef2f2;border-left:5px solid #ef4444;padding:12px;margin-bottom:15px;border-radius:4px">'
                '<div style="color:#b91c1c;font-weight:700;margin-bottom:5px">🛡️ ADMINISTRATIVE OVERRIDE CONTROL</div>'
                '<div style="color:#7f1d1d;font-size:12px">'
                '• Block users to prevent all platform access. <br>'
                '• Set <b>AI Limit</b> to 0 for system default (5/day). <br>'
                '• Set <b>Resume Limit</b> to 0 for system default (2/day). <br>'
                '• You can manually reset "Resumes Created Today" by setting it to 0.'
                '</div>'
                '</div>'
            ),
        }),
        ('📝 Detailed Profile Components', {
            'fields': ('profile_quick_links',),
            'description': 'Quickly jump to this user’s specific profile datasets.'
        }),
        ('🕒 Activity Timeline (Read-only)', {
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
    
    def avatar_thumbnail(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;border:1px solid #e5e7eb" />', obj.profile_image.url)
        return format_html('<div style="width:30px;height:30px;border-radius:50%;background:#f3f4f6;display:flex;align-items:center;justify-content:center;color:#9ca3af;font-size:10px;font-weight:700">{}</div>', obj.email[0].upper())
    avatar_thumbnail.short_description = '📸'

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

    def location_badge(self, obj):
        try:
            profile = obj.profile
            if not profile.city and not profile.country:
                return '—'
            location = f"{profile.city}, {profile.country}".strip(', ')
            return format_html('<span style="color:#6b7280;font-size:11px">🌍 {}</span>', location)
        except:
            return '—'
    location_badge.short_description = 'Location'

    def email_verified_badge(self, obj):
        verified = EmailAddress.objects.filter(user=obj, verified=True).exists()
        if verified:
            return format_html('<span style="color:#16a34a;font-weight:700">✅ Verified</span>')
        return format_html('<span style="color:#dc2626;font-weight:500">❌ Unverified</span>')
    email_verified_badge.short_description = '📧 Email'

    def last_seen_delta(self, obj):
        if not obj.last_activity:
            return 'Never'
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(obj.last_activity)
    last_seen_delta.short_description = '🕒 Last Seen'

    def resume_count(self, obj):
        count = obj.resumes.filter(is_active=True).count()
        if count == 0:
            return format_html('<span style="color:#9ca3af">0</span>')
        url = f'/admin/resumes/resume/?user__id__exact={obj.id}'
        return format_html('<a href="{}" style="font-weight:600;color:#6366f1">{} resume{}</a>', url, count, 's' if count != 1 else '')
    resume_count.short_description = '📄 Resumes'

    def ai_calls_today(self, obj):
        from resumes.models import AIPromptLog
        today = now().date()
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
        today = now().date()
        logs = AIPromptLog.objects.filter(user=obj)
        total = logs.count()
        today_count = logs.filter(created_at__date=today).count()
        by_type = logs.values('prompt_type').annotate(n=Count('id')).order_by('-n')
        lines = [f'Total AI calls: {total}', f'Today: {today_count}', '---']
        for row in by_type:
            lines.append(f'{row["prompt_type"]}: {row["n"]}')
        return '\n'.join(lines)
    ai_usage_summary.short_description = 'AI Usage Breakdown'

    def stats_visual(self, obj):
        from resumes.models import AIPromptLog
        today = now().date()
        total_ai = AIPromptLog.objects.filter(user=obj).count()
        today_ai = AIPromptLog.objects.filter(user=obj, created_at__date=today).count()
        ai_limit = obj.api_daily_limit if obj.api_daily_limit > 0 else 5
        
        total_res = obj.resumes.count()
        today_res = obj.resumes_created_today
        res_limit = obj.resume_daily_limit if obj.resume_daily_limit > 0 else 2
        
        # Calculate percentages for meters
        ai_percent = min(round((today_ai / ai_limit) * 100), 100) if ai_limit > 0 else 0
        res_percent = min(round((today_res / res_limit) * 100), 100) if res_limit > 0 else 0
        
        ai_color = "#10b981" if ai_percent < 70 else ("#f59e0b" if ai_percent < 95 else "#ef4444")
        res_color = "#6366f1" if res_percent < 70 else ("#f59e0b" if res_percent < 95 else "#ef4444")

        dashboard_html = format_html(
            '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:15px;padding:15px;background:#1e293b;border-radius:12px;border:1px solid #334155">'
            '<!-- AI Meter -->'
            '<div style="text-align:center">'
            '<div style="color:#9ca3af;font-size:11px;text-transform:uppercase;margin-bottom:8px">⚡ AI Usage (Today)</div>'
            '<div style="position:relative;height:8px;background:#334155;border-radius:4px;overflow:hidden;margin-bottom:8px">'
            '<div style="width:{}%;height:100%;background:{};"></div>'
            '</div>'
            '<div style="color:white;font-size:18px;font-weight:700">{}/{}</div>'
            '<div style="color:#64748b;font-size:10px">Total calls: {}</div>'
            '</div>'
            '<!-- Resume Meter -->'
            '<div style="text-align:center">'
            '<div style="color:#9ca3af;font-size:11px;text-transform:uppercase;margin-bottom:8px">📄 Resumes (Today)</div>'
            '<div style="position:relative;height:8px;background:#334155;border-radius:4px;overflow:hidden;margin-bottom:8px">'
            '<div style="width:{}%;height:100%;background:{};"></div>'
            '</div>'
            '<div style="color:white;font-size:18px;font-weight:700">{}/{}</div>'
            '<div style="color:#64748b;font-size:10px">Total items: {}</div>'
            '</div>'
            '<!-- Account Status -->'
            '<div style="text-align:center;border-left:1px solid #334155">'
            '<div style="color:#9ca3af;font-size:11px;text-transform:uppercase;margin-bottom:8px">🌍 Identity</div>'
            '<div style="color:#eff6ff;font-weight:600;margin-bottom:2px">{} logins</div>'
            '<div style="color:#6366f1;font-size:10px">ID: #{}</div>'
            '</div>'
            '</div>',
            ai_percent, ai_color, today_ai, ai_limit, total_ai,
            res_percent, res_color, today_res, res_limit, total_res,
            obj.login_count, obj.id
        )
        return dashboard_html
    stats_visual.short_description = 'User Health Metrics'

    def profile_quick_links(self, obj):
        links = [
            ('🎓 Education', 'users_education_changelist', 'profile__user'),
            ('🏢 Experience', 'users_experience_changelist', 'profile__user'),
            ('⚡ Skills', 'users_skill_changelist', 'profile__user'),
            ('📜 Certs', 'users_certification_changelist', 'profile__user'),
            ('🚀 Projects', 'users_project_changelist', 'profile__user'),
        ]
        html = ['<div style="display:flex;gap:10px;flex-wrap:wrap">']
        for label, view_name, param in links:
            url = f"/admin/users/{view_name.split('_')[1]}/?{param}={obj.id}"
            html.append(
                f'<a href="{url}" style="padding:6px 12px;background:#334155;color:white;border-radius:6px;font-size:12px;text-decoration:none;font-weight:600;border:1px solid #475569">'
                f'{label}</a>'
            )
        html.append('</div>')
        return format_html("".join(html))
    profile_quick_links.short_description = 'Quick Access'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('resumes', 'ai_logs')


# ─── Resume Admin ─────────────────────────────────────────────────────────────

# ─── Profile Components Admins ────────────────────────────────────────────────

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('school_icon', 'institution', 'degree_badge', 'field_of_study', 'user_avatar_link')
    search_fields = ('institution', 'degree', 'profile__user__email')
    list_filter = ('degree', 'profile__user')
    raw_id_fields = ('profile',)

    def school_icon(self, obj):
        return format_html('<span style="font-size:18px">🎓</span>')
    school_icon.short_description = ''

    def degree_badge(self, obj):
        return format_html('<span style="color:#6366f1;font-weight:700">{}</span>', obj.degree)
    degree_badge.short_description = 'Degree'

    def user_avatar_link(self, obj):
        user = obj.profile.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">👤 {}</a>', url, user.email)
    user_avatar_link.short_description = 'User'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company_icon', 'company', 'title_badge', 'duration_badge', 'status_badge', 'user_avatar_link')
    search_fields = ('company', 'title', 'profile__user__email')
    list_filter = ('is_current', 'profile__user')
    raw_id_fields = ('profile',)

    def company_icon(self, obj):
        return format_html('<span style="font-size:18px">🏢</span>')
    company_icon.short_description = ''

    def title_badge(self, obj):
        return format_html('<b style="color:white">{}</b>', obj.title)
    title_badge.short_description = 'Position'

    def duration_badge(self, obj):
        start = obj.start_date.strftime('%b %Y') if obj.start_date else '?'
        end = "Present" if obj.is_current else (obj.end_date.strftime('%b %Y') if obj.end_date else '—')
        return format_html('<span style="color:#9ca3af;font-size:11px">{} - {}</span>', start, end)
    duration_badge.short_description = 'Duration'

    def status_badge(self, obj):
        if obj.is_current:
            return format_html('<span style="color:white;background:#10b981;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">CURRENT</span>')
        return format_html('<span style="color:#9ca3af;font-size:10px">PAST</span>')
    status_badge.short_description = 'Status'

    def user_avatar_link(self, obj):
        user = obj.profile.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">👤 {}</a>', url, user.email)
    user_avatar_link.short_description = 'User'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name_badge', 'category', 'proficiency_badge', 'user_avatar_link')
    list_filter = ('category', 'proficiency', 'profile__user')
    search_fields = ('name', 'profile__user__email')
    raw_id_fields = ('profile',)

    def name_badge(self, obj):
        return format_html('<b style="color:white">{}</b>', obj.name)
    name_badge.short_description = 'Skill'

    def proficiency_badge(self, obj):
        colors = {
            'Expert': '#7c3aed',
            'Intermediate': '#10b981',
            'Beginner': '#f59e0b',
        }
        color = colors.get(obj.proficiency, '#6366f1')
        return format_html('<span style="color:white;background:{};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700">{}</span>', color, obj.proficiency)
    proficiency_badge.short_description = 'Level'

    def user_avatar_link(self, obj):
        user = obj.profile.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">👤 {}</a>', url, user.email)
    user_avatar_link.short_description = 'User'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('cert_icon', 'name', 'issuer_badge', 'date_badge', 'user_avatar_link')
    search_fields = ('name', 'issuer', 'profile__user__email')
    list_filter = ('profile__user',)
    raw_id_fields = ('profile',)

    def cert_icon(self, obj):
        return format_html('<span style="font-size:18px">📜</span>')
    cert_icon.short_description = ''

    def issuer_badge(self, obj):
        return format_html('<span style="color:#0ea5e9;font-weight:600">{}</span>', obj.issuer)
    issuer_badge.short_description = 'Issuer'

    def date_badge(self, obj):
        return obj.date_obtained.strftime('%Y-%m-%d') if obj.date_obtained else '—'
    date_badge.short_description = 'Date'

    def user_avatar_link(self, obj):
        user = obj.profile.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">👤 {}</a>', url, user.email)
    user_avatar_link.short_description = 'User'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('proj_icon', 'name', 'technologies_badge', 'user_avatar_link')
    search_fields = ('name', 'technologies', 'profile__user__email')
    list_filter = ('profile__user',)
    raw_id_fields = ('profile',)

    def proj_icon(self, obj):
        return format_html('<span style="font-size:18px">🚀</span>')
    proj_icon.short_description = ''

    def technologies_badge(self, obj):
        tags = [t.strip() for t in obj.technologies.split(',')]
        badges = []
        for tag in tags[:3]: # Show first 3 tags
            badges.append(f'<span style="color:#9ca3af;background:#334155;padding:1px 6px;border-radius:4px;font-size:10px;margin-right:3px">{tag}</span>')
        if len(tags) > 3:
            badges.append('<span style="color:#6b7280;font-size:10px">...</span>')
        return format_html("".join(badges))
    technologies_badge.short_description = 'Tech Stack'

    def user_avatar_link(self, obj):
        user = obj.profile.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">👤 {}</a>', url, user.email)
    user_avatar_link.short_description = 'User'


# ─── Email Address Admin Override ───────────────────────────────────────────

try:
    admin.site.unregister(EmailAddress)
except admin.sites.NotRegistered:
    pass

@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_link', 'verified_badge', 'primary_badge')
    list_filter = ('verified', 'primary')
    search_fields = ('email', 'user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    ordering = ('email',)

    def user_link(self, obj):
        user = obj.user
        url = reverse('admin:users_customuser_change', args=[user.id])
        status = ""
        if user.is_blocked:
            status = " 🚫"
        elif user.is_staff:
            status = " ⚙️"
        return format_html('<a href="{}" style="color:#6366f1;font-weight:500">{}</a>{}', url, user.email, status)
    user_link.short_description = '👤 User'

    def verified_badge(self, obj):
        if obj.verified:
            return format_html('<span style="color:white;background:#16a34a;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">✅ Verified</span>')
        return format_html('<span style="color:white;background:#ef4444;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">❌ Unverified</span>')
    verified_badge.short_description = 'Verification'

    def primary_badge(self, obj):
        if obj.primary:
            return format_html('<span style="color:white;background:#7c3aed;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">⭐ Primary</span>')
        return format_html('<span style="color:#9ca3af;font-size:11px">Secondary</span>')
    primary_badge.short_description = 'Primary'

    def changelist_view(self, request, extra_context=None):
        # Calculate mathematical stats for the dashboard
        total = self.model.objects.count()
        if total > 0:
            verified_count = self.model.objects.filter(verified=True).count()
            primary_count = self.model.objects.filter(primary=True).count()
            unique_users = self.model.objects.values('user').distinct().count()
            
            verified_pc = (verified_count / total) * 100
            primary_pc = (primary_count / total) * 100
            
            # Simple domain breakdown
            gmail_count = self.model.objects.filter(email__icontains='@gmail.com').count()
            gmail_pc = (gmail_count / total) * 100

            # Pre-format as strings to avoid format_html specifier issues with SafeString
            verified_str = f"{verified_pc:.1f}%"
            primary_str = f"{primary_pc:.1f}%"
            gmail_str = f"{gmail_pc:.1f}%"

            stats_html = format_html(
                '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:15px;margin-bottom:20px;padding:15px;background:#1e293b;border-radius:10px;border:1px solid #334155">'
                '<div style="text-align:center"><div style="color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px">📊 Total Emails</div><div style="color:white;font-size:24px;font-weight:700">{}</div></div>'
                '<div style="text-align:center"><div style="color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px">✅ Verified Rate</div><div style="color:#10b981;font-size:24px;font-weight:700">{}</div></div>'
                '<div style="text-align:center"><div style="color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px">⭐ Primary Rate</div><div style="color:#7c3aed;font-size:24px;font-weight:700">{}</div></div>'
                '<div style="text-align:center"><div style="color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px">👤 Unique Users</div><div style="color:white;font-size:24px;font-weight:700">{}</div></div>'
                '<div style="text-align:center"><div style="color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px">📧 Gmail Usage</div><div style="color:#0ea5e9;font-size:24px;font-weight:700">{}</div></div>'
                '</div>',
                total, verified_str, primary_str, unique_users, gmail_str
            )
            
            extra_context = extra_context or {}
            extra_context['stats_dashboard'] = stats_html
            
        return super().changelist_view(request, extra_context=extra_context)


# ─── Social Accounts Admin Overrides ────────────────────────────────────────

# 1. Social Accounts
try:
    admin.site.unregister(SocialAccount)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialAccount)
class CustomSocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'provider_badge', 'uid_short', 'last_login_status')
    list_filter = ('provider',)
    search_fields = ('user__email', 'uid', 'extra_data')
    readonly_fields = ('extra_data_formatted',)
    raw_id_fields = ('user',)

    def user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600">{}</a>', url, obj.user.email)
    user_link.short_description = '👤 User'

    def provider_badge(self, obj):
        colors = {
            'google': '#ea4335',
            'github': '#24292e',
            'facebook': '#1877f2',
            'linkedin': '#0a66c2'
        }
        color = colors.get(obj.provider.lower(), '#6366f1')
        icon = ""
        if 'google' in obj.provider.lower(): icon = "G"
        elif 'github' in obj.provider.lower(): icon = "GH"
        
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700">{} {}</span>',
            color, icon, obj.provider.upper()
        )
    provider_badge.short_description = 'Provider'

    def uid_short(self, obj):
        return f"{obj.uid[:10]}..." if len(obj.uid) > 10 else obj.uid
    uid_short.short_description = 'Social ID'

    def last_login_status(self, obj):
        return obj.user.last_login.strftime('%Y-%m-%d %H:%M') if obj.user.last_login else "Never"
    last_login_status.short_description = 'Last Sync'

    def extra_data_formatted(self, obj):
        content = json.dumps(obj.extra_data, indent=4)
        return format_html('<pre style="background:#0f172a;color:#38bdf8;padding:15px;border-radius:8px">{}</pre>', content)
    extra_data_formatted.short_description = 'Deep Profile Data'


# 2. Social Applications
try:
    admin.site.unregister(SocialApp)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialApp)
class CustomSocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider_badge', 'client_id_status', 'secret_status')
    list_filter = ('provider',)
    
    def provider_badge(self, obj):
        return format_html('<b style="color:#6366f1">{}</b>', obj.provider.upper())
    provider_badge.short_description = 'Provider'

    def client_id_status(self, obj):
        if obj.client_id:
            return format_html('<span style="color:#10b981">● Configured</span>')
        return format_html('<span style="color:#ef4444">○ Missing ID</span>')
    client_id_status.short_description = 'Client ID'

    def secret_status(self, obj):
        if obj.secret:
            return format_html('<span style="color:#10b981">● Securely Set</span>')
        return format_html('<span style="color:#ef4444">○ Missing Secret</span>')
    secret_status.short_description = 'Secret'


# 3. Social Tokens
try:
    admin.site.unregister(SocialToken)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialToken)
class CustomSocialTokenAdmin(admin.ModelAdmin):
    list_display = ('account', 'app', 'expiry_badge', 'token_short')
    list_filter = ('app__provider', 'expires_at')
    raw_id_fields = ('account', 'app')

    def expiry_badge(self, obj):
        if not obj.expires_at:
            return format_html('<span style="color:#9ca3af">Never Expires</span>')
        if obj.expires_at < now():
            return format_html('<span style="color:white;background:#ef4444;padding:2px 8px;border-radius:10px;font-size:11px">Expired</span>')
        return format_html('<span style="color:white;background:#10b981;padding:2px 8px;border-radius:10px;font-size:11px">Active</span>')
    expiry_badge.short_description = 'Status'

    def token_short(self, obj):
        return f"{obj.token[:15]}..."
    token_short.short_description = 'Token Preview'
