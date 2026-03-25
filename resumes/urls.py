from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/create/', views.create_resume, name='create_resume'),
    path('resume/<int:resume_id>/builder/', views.resume_builder, name='resume_builder'),
    path('resume/<int:resume_id>/save/', views.save_resume, name='save_resume'),
    path('resume/<int:resume_id>/history/', views.resume_history, name='resume_history'),
    path('resume/<int:resume_id>/rollback/<int:version_id>/', views.rollback_version, name='rollback_version'),
    path('resume/<int:resume_id>/duplicate/', views.duplicate_resume, name='duplicate_resume'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/<int:resume_id>/preview/', views.preview_resume_pdf, name='preview_resume_pdf'),
    path('resume/<int:resume_id>/download/<str:file_format>/', views.download_resume, name='download_resume'),
    path('resume/share/<uuid:token>/', views.public_resume_view, name='public_resume'),
    path('resume/share/<uuid:token>/preview/', views.public_preview_resume_pdf, name='public_preview_resume_pdf'),
    path('resume/share/<uuid:token>/download/', views.public_download_resume, name='public_download_resume'),
    # Admin-only version preview/download
    path('resume-admin/version/<int:version_id>/pdf/', views.admin_version_pdf, name='admin_version_pdf'),
    path('resume-admin/resume/<int:resume_id>/pdf/', views.admin_current_pdf, name='admin_current_pdf'),
]
