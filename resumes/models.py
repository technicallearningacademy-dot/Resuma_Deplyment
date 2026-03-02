"""
Resume and version history models.
"""
from django.db import models
from django.conf import settings
import uuid


class Resume(models.Model):
    """Main resume model."""
    TEMPLATE_CHOICES = [
        ('modern_ats_clean', 'Modern ATS Clean'),
        ('minimal_academic', 'Minimal Academic'),
        ('corporate_executive', 'Corporate Executive'),
        ('creative_designer', 'Creative Designer'),
        ('technical_developer', 'Technical Developer'),
        ('startup_founder', 'Startup Founder'),
        ('data_scientist', 'Data Scientist'),
        ('marketing_pro', 'Marketing Pro'),
        ('legal_standard', 'Legal Standard'),
        ('medical_clinical', 'Medical Clinical'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=300, default='My Resume')
    template_name = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='modern_ats_clean')
    latex_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True, help_text='Allow anyone with the link to view and download this resume')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, help_text='Unique token for the public share link')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @property
    def latest_pdf_url(self):
        """Returns the URL of the latest version's PDF file, if it exists."""
        latest_version = self.versions.filter(pdf_file__isnull=False).exclude(pdf_file='').first()
        if latest_version and latest_version.pdf_file:
            return latest_version.pdf_file.url
        return None

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
