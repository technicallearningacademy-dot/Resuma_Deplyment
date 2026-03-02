"""
Resume monitoring admin — tracks all resumes and AI prompt logs per user.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from .models import Resume, ResumeVersion, AIPromptLog, UploadedCV


# ─── Resume Admin ─────────────────────────────────────────────────────────────

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user_link', 'template_badge', 'version_count',
        'is_active', 'created_at', 'updated_at',
    )
    list_filter = ('template_name', 'is_active', 'created_at')
    search_fields = ('title', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'version_count_display')
    ordering = ('-updated_at',)
    list_per_page = 40

    fieldsets = (
        ('📄 Resume Info', {'fields': ('user', 'title', 'template_name', 'is_active')}),
        ('✏️ Content', {'fields': ('latex_content',), 'classes': ('collapse',)}),
        ('📊 Stats', {'fields': ('created_at', 'updated_at', 'version_count_display'), 'classes': ('collapse',)}),
    )

    def user_link(self, obj):
        url = f'/admin/users/customuser/{obj.user.id}/change/'
        label = obj.user.email
        blocked = getattr(obj.user, 'is_blocked', False)
        color = '#dc2626' if blocked else '#6366f1'
        return format_html('<a href="{}" style="color:{};font-weight:500">{}</a>', url, color, label)
    user_link.short_description = '👤 User'

    def template_badge(self, obj):
        colors = {
            'modern_ats_clean': '#0ea5e9',
            'minimal_academic': '#6b7280',
            'corporate_executive': '#16a34a',
            'creative_designer': '#0d9488',
            'technical_developer': '#7c3aed',
        }
        color = colors.get(obj.template_name, '#6366f1')
        label = obj.get_template_name_display()
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, label
        )
    template_badge.short_description = '🎨 Template'

    def version_count(self, obj):
        count = obj.versions.count()
        return format_html('<span style="font-weight:600">{}</span>', count)
    version_count.short_description = '🔄 Versions'

    def version_count_display(self, obj):
        return obj.versions.count()
    version_count_display.short_description = 'Version Count'


# ─── AI Prompt Log Admin (Core Activity Monitor) ──────────────────────────────

@admin.register(AIPromptLog)
class AIPromptLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'user_link', 'action_badge', 'model_used',
        'resume_link', 'prompt_preview', 'tokens_used',
    )
    list_filter = ('prompt_type', 'model_used', 'created_at')
    search_fields = ('user__email', 'prompt_type', 'prompt')
    readonly_fields = ('user', 'resume', 'prompt_type', 'model_used', 'tokens_used', 'created_at', 'prompt', 'response')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    def user_link(self, obj):
        url = f'/admin/users/customuser/{obj.user.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1;font-weight:500">{}</a>', url, obj.user.email)
    user_link.short_description = '👤 User'

    def action_badge(self, obj):
        styles = {
            'generate': ('⚡', '#7c3aed'),
            'enhance':  ('✨', '#0d9488'),
            'optimize': ('🎯', '#ea580c'),
            'extract':  ('📤', '#0ea5e9'),
        }
        icon, color = styles.get(obj.prompt_type, ('🤖', '#6b7280'))
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;border-radius:10px;font-size:11px">{} {}</span>',
            color, icon, obj.prompt_type.title()
        )
    action_badge.short_description = '🤖 Action'

    def resume_link(self, obj):
        if not obj.resume:
            return '—'
        url = f'/admin/resumes/resume/{obj.resume.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1">{}</a>', url, obj.resume.title)
    resume_link.short_description = '📄 Resume'

    def prompt_preview(self, obj):
        text = (obj.prompt or '')[:80]
        return format_html('<span style="color:#9ca3af;font-size:11px">{}</span>', text + '…' if len(obj.prompt or '') > 80 else text)
    prompt_preview.short_description = 'Prompt Preview'


# ─── Version History Admin ────────────────────────────────────────────────────

@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'version_number', 'change_note', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('resume__title', 'resume__user__email', 'change_note')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ─── Uploaded CVs ─────────────────────────────────────────────────────────────

@admin.register(UploadedCV)
class UploadedCVAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'uploaded_at')
    search_fields = ('original_filename', 'user__email')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
