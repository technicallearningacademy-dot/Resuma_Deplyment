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
        'updated_at', 'user_link', 'title', 'builder_link', 'view_live',
        'template_badge', 'version_count', 'share_status', 'last_ai_model',
        'is_active',
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

    def builder_link(self, obj):
        url = f'/resume/{obj.id}/builder/'
        return format_html(
            '<a href="{}" target="_blank" style="background:#6366f1;color:white;padding:3px 8px;border-radius:5px;font-size:11px;text-decoration:none">🛠️ Builder</a>',
            url
        )
    builder_link.short_description = '🛠️ Tools'

    def view_live(self, obj):
        url = f'/resume-admin/resume/{obj.id}/pdf/'
        return format_html(
            '<a href="{}" target="_blank" style="background:#0ea5e9;color:white;padding:3px 8px;border-radius:5px;font-size:11px;text-decoration:none">📄 Preview</a>',
            url
        )
    view_live.short_description = 'Live'

    def share_status(self, obj):
        if not obj.is_public:
            return format_html('<span style="color:#9ca3af;font-size:11px">🔒 Private</span>')
        
        # Determine the host
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '')
        if not site_url:
            site_url = "http://localhost:8000"
            
        share_url = f"{site_url}/resume/share/{obj.share_token}/"
        return format_html(
            '<a href="{}" target="_blank" style="color:#10b981;font-size:11px;display:flex;align-items:center;gap:4px">🔗 Public</a>',
            share_url
        )
    share_status.short_description = '🔗 Share'

    def last_ai_model(self, obj):
        last_log = obj.ai_logs.first()
        if not last_log:
            return '—'
        model = last_log.model_used
        color = '#7c3aed' if 'gemini' in model.lower() else '#0ea5e9'
        return format_html('<span style="color:{};font-family:monospace;font-size:11px">{}</span>', color, model)
    last_ai_model.short_description = '🤖 AI'

    def version_count_display(self, obj):
        return obj.versions.count()
    version_count_display.short_description = 'Version Count'


# ─── AI Prompt Log Admin (Core Activity Monitor) ──────────────────────────────

@admin.register(AIPromptLog)
class AIPromptLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'user_link', 'action_badge', 'model_used',
        'resume_link', 'prompt_preview', 'response_preview', 'tokens_badge',
    )
    list_filter = ('prompt_type', 'model_used', 'created_at')
    search_fields = ('user__email', 'prompt_type', 'prompt', 'response')
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
            'chat':     ('💬', '#6366f1'),
            'edit':     ('📝', '#8b5cf6'),
            'rewrite':  ('✍️', '#f43f5e'),
        }
        icon, color = styles.get(obj.prompt_type, ('🤖', '#6b7280'))
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">{} {}</span>',
            color, icon, obj.prompt_type.title()
        )
    action_badge.short_description = '🤖 Action'

    def tokens_badge(self, obj):
        count = obj.tokens_used
        if count == 0:
            color = '#9ca3af'  # Gray
        elif count < 1000:
            color = '#10b981'  # Green
        elif count < 5000:
            color = '#f59e0b'  # Amber
        else:
            color = '#ef4444'  # Red
            
        return format_html(
            '<span style="color:{};font-weight:700;font-family:monospace">{}</span>',
            color, f"{count:,}"
        )
    tokens_badge.short_description = '🪙 Tokens'

    def resume_link(self, obj):
        if not obj.resume:
            return '—'
        url = f'/admin/resumes/resume/{obj.resume.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1">{}</a>', url, obj.resume.title)
    resume_link.short_description = '📄 Resume'

    def prompt_preview(self, obj):
        text = (obj.prompt or '')[:60]
        return format_html('<span style="color:#9ca3af;font-size:11px">{}</span>', text + '...' if len(obj.prompt or '') > 60 else text)
    prompt_preview.short_description = 'Prompt'

    def response_preview(self, obj):
        text = (obj.response or '')[:60]
        return format_html('<span style="color:#6b7280;font-size:11px;font-style:italic">{}</span>', text + '...' if len(obj.response or '') > 60 else text)
    response_preview.short_description = 'AI Response'


# ─── Version History Admin ────────────────────────────────────────────────────

@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'user_link', 'resume_link', 'version_number', 
        'view_pdf', 'download_pdf', 'change_note', 'latex_preview'
    )
    list_filter = ('resume__user', 'created_at')
    search_fields = ('resume__title', 'resume__user__email', 'change_note', 'latex_content')
    ordering = ('-created_at',)
    readonly_fields = ('resume', 'version_number', 'change_note', 'latex_content', 'created_at')

    def user_link(self, obj):
        user = obj.resume.user
        url = f'/admin/users/customuser/{user.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1;font-weight:500">{}</a>', url, user.email)
    user_link.short_description = '👤 User'

    def resume_link(self, obj):
        url = f'/admin/resumes/resume/{obj.resume.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1">{}</a>', url, obj.resume.title)
    resume_link.short_description = '📄 Resume'

    def view_pdf(self, obj):
        url = f'/resume-admin/version/{obj.id}/pdf/'
        return format_html(
            '<a href="{}" target="_blank" style="background:#6366f1;color:white;padding:3px 10px;border-radius:5px;font-size:11px;text-decoration:none">👁️ View PDF</a>',
            url
        )
    view_pdf.short_description = 'Preview'

    def download_pdf(self, obj):
        url = f'/resume-admin/version/{obj.id}/pdf/?download=1'
        return format_html(
            '<a href="{}" style="background:#10b981;color:white;padding:3px 10px;border-radius:5px;font-size:11px;text-decoration:none">📥 Download</a>',
            url
        )
    download_pdf.short_description = 'Download'

    def latex_preview(self, obj):
        text = (obj.latex_content or '')[:50]
        return format_html('<code style="color:#9ca3af;font-size:10px">{}...</code>', text)
    latex_preview.short_description = '📄 Code Preview'


# ─── Uploaded CVs ─────────────────────────────────────────────────────────────

@admin.register(UploadedCV)
class UploadedCVAdmin(admin.ModelAdmin):
    list_display = (
        'uploaded_at', 'user_link', 'original_filename', 
        'download_file', 'extraction_status', 'data_preview'
    )
    list_filter = ('uploaded_at', 'user')
    search_fields = ('original_filename', 'user__email', 'extracted_data')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at', 'user', 'file', 'original_filename', 'extracted_data')

    def user_link(self, obj):
        user = obj.user
        url = f'/admin/users/customuser/{user.id}/change/'
        return format_html('<a href="{}" style="color:#6366f1;font-weight:500">{}</a>', url, user.email)
    user_link.short_description = '👤 User'

    def download_file(self, obj):
        if not obj.file:
            return '—'
        return format_html(
            '<a href="{}" target="_blank" style="background:#0ea5e9;color:white;padding:3px 10px;border-radius:5px;font-size:11px;text-decoration:none">📥 Download</a>',
            obj.file.url
        )
    download_file.short_description = 'File'

    def extraction_status(self, obj):
        if obj.extracted_data:
            return format_html(
                '<span style="color:white;background:#10b981;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">✅ Processed</span>'
            )
        return format_html(
            '<span style="color:white;background:#6b7280;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">⚪ Pending</span>'
        )
    extraction_status.short_description = 'Status'

    def data_preview(self, obj):
        if not obj.extracted_data:
            return '—'
        import json
        try:
            # Show first 80 chars of the JSON string for context
            data_str = json.dumps(obj.extracted_data)
            text = (data_str[:80] + '...') if len(data_str) > 80 else data_str
            return format_html('<code style="color:#6b7280;font-size:10px">{}</code>', text)
        except:
            return 'Invalid Data'
    data_preview.short_description = 'Extracted Data'
