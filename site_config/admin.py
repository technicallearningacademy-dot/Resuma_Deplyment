from django.contrib import admin
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.html import format_html
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'default_theme', 'enable_pink_theme', 'enable_violet_theme')
    
    # Only allow 1 instance
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


# ─── Sites Admin Override ───────────────────────────────────────────────────

try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name', 'status_badge', 'visit_site')
    search_fields = ('domain', 'name')
    ordering = ('domain',)

    def status_badge(self, obj):
        # Clean the settings URL for comparison
        clean_site_url = settings.SITE_URL.replace('https://', '').replace('http://', '').strip('/')
        
        if obj.domain == clean_site_url or (not clean_site_url and obj.domain == '127.0.0.1:8000'):
            return format_html('<span style="color:white;background:#16a34a;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">✅ Synced with .env</span>')
        
        return format_html('<span style="color:white;background:#f59e0b;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">⚠️ Out of Sync</span>')
    status_badge.short_description = 'Configuration Status'

    def visit_site(self, obj):
        protocol = 'https' if 'ngrok' in obj.domain else 'http'
        url = f"{protocol}://{obj.domain}"
        return format_html('<a href="{}" target="_blank" style="color:#6366f1;font-weight:600;text-decoration:none">🌐 Visit Site</a>', url)
    visit_site.short_description = 'Live Link'
