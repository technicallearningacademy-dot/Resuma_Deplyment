from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from users.views import landing_page
from users.admin_views import admin_monitor, admin_monitor_api, update_user_limits

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-monitor/', admin_monitor, name='admin_monitor'),
    path('admin-monitor/api/', admin_monitor_api, name='admin_monitor_api'),
    path('admin-monitor/set-limits/', update_user_limits, name='admin_monitor_set_limits'),
    path('', landing_page, name='landing'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('', include('users.urls')),
    path('', include('resumes.urls')),
    path('ai/', include('ai_services.urls')),
    path('engine/', include('templates_engine.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customizing Admin Panel
admin.site.site_header = "ResumeForge AI Admin"
admin.site.site_title = "ResumeForge Admin Portal"
admin.site.index_title = "Welcome to the ResumeForge Management System"
