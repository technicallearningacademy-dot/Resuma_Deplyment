"""
Resume and version history models.
"""
from django.db import models
from django.conf import settings


class Resume(models.Model):
    """Main resume model."""
    TEMPLATE_CHOICES = [
        ('modern_ats_clean', 'Modern ATS Clean'),
        ('minimal_academic', 'Minimal Academic'),
        ('corporate_executive', 'Corporate Executive'),
        ('creative_designer', 'Creative Designer'),
        ('technical_developer', 'Technical Developer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=300, default='My Resume')
    template_name = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='modern_ats_clean')
    latex_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} - {self.user.email}'


class ResumeVersion(models.Model):
    """Stores version history for a resume."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    latex_content = models.TextField()
    pdf_file = models.FileField(upload_to='resumes/pdf/', blank=True, null=True)
    docx_file = models.FileField(upload_to='resumes/docx/', blank=True, null=True)
    change_note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['resume', 'version_number']

    def __str__(self):
        return f'{self.resume.title} v{self.version_number}'


class AIPromptLog(models.Model):
    """Logs AI interactions for debugging and history."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_logs')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_logs')
    prompt_type = models.CharField(max_length=50)  # generate, enhance, extract, optimize
    prompt = models.TextField()
    response = models.TextField()
    model_used = models.CharField(max_length=100, default='gemini-2.0-flash')
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.prompt_type} - {self.user.email} - {self.created_at}'


class UploadedCV(models.Model):
    """Stores uploaded CVs for data extraction."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_cvs')
    file = models.FileField(upload_to='uploaded_cvs/')
    original_filename = models.CharField(max_length=300)
    extracted_data = models.JSONField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.original_filename} - {self.user.email}'
