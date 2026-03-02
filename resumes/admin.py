from django.contrib import admin
from .models import Resume, ResumeVersion, AIPromptLog, UploadedCV


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'template_name', 'is_active', 'updated_at')
    list_filter = ('template_name', 'is_active')
    search_fields = ('title', 'user__email')


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'version_number', 'created_at')


@admin.register(AIPromptLog)
class AIPromptLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'prompt_type', 'model_used', 'created_at')
    list_filter = ('prompt_type', 'model_used')


@admin.register(UploadedCV)
class UploadedCVAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'uploaded_at')
