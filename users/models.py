"""
Custom User model and Profile models for the AI Resume Builder.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import random
import string


class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email instead of username."""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False, help_text='Block user from accessing the platform')
    api_daily_limit = models.PositiveIntegerField(
        default=0,
        help_text='Custom daily AI prompt limit. 0 = use system default (5)'
    )
    resume_daily_limit = models.PositiveIntegerField(
        default=0,
        help_text='Custom daily resume creation limit. 0 = use system default (1)'
    )
    login_count = models.PositiveIntegerField(default=0, help_text='Total number of logins')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True, help_text='Last time the user made any request')
    date_joined = models.DateTimeField(default=timezone.now)

    # Tracking daily limits independently of database objects
    resumes_created_today = models.PositiveIntegerField(default=0)
    last_resume_creation_date = models.DateField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def get_resume_daily_limit(self):
        return self.resume_daily_limit if self.resume_daily_limit > 0 else 2

    def get_ai_daily_limit(self):
        """Effective daily AI prompt limit for this user."""
        return self.api_daily_limit if self.api_daily_limit > 0 else 5

    def can_create_resume_today(self):
        """Check if user can create a resume today based on their personal limit."""
        today = timezone.now().date()
        if self.last_resume_creation_date != today:
            return True
        return self.resumes_created_today < self.get_resume_daily_limit()

    def increment_resume_creation(self):
        """Record that a user created a resume today."""
        today = timezone.now().date()
        if self.last_resume_creation_date != today:
            self.last_resume_creation_date = today
            self.resumes_created_today = 1
        else:
            self.resumes_created_today += 1
        self.save()


class UserProfile(models.Model):
    """Extended profile data for structured CV information."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    summary = models.TextField(blank=True, help_text='Professional summary / objective')
    job_title = models.CharField(max_length=200, blank=True, help_text='Desired job title')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile: {self.user.email}'


class EmailOTP(models.Model):
    """Stores 6-digit OTP codes for email verification."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """OTP is valid for 15 minutes and only if not used."""
        if self.is_used:
            return False
        expiration_time = self.created_at + timezone.timedelta(minutes=15)
        return timezone.now() <= expiration_time

    @classmethod
    def generate_otp(cls, user):
        """Generates a secure 6-digit OTP for the user."""
        # Invalidate old OTPs
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(user=user, code=code)

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class Education(models.Model):
    """Education entries for user profile."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education_entries')
    institution = models.CharField(max_length=300)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    gpa = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.degree} @ {self.institution}'


class Experience(models.Model):
    """Work experience entries for user profile."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experience_entries')
    company = models.CharField(max_length=300)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    achievements = models.TextField(blank=True, help_text='Key achievements, one per line')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} @ {self.company}'


class Skill(models.Model):
    """Skills for user profile."""
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skill'),
        ('language', 'Language'),
        ('tool', 'Tool / Software'),
    ]
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')

    def __str__(self):
        return self.name


class Certification(models.Model):
    """Certifications for user profile."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=300)
    issuer = models.CharField(max_length=200)
    date_obtained = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    """Projects for user profile."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=300)
    description = models.TextField()
    technologies = models.CharField(max_length=500, blank=True, help_text='Comma separated')
    url = models.URLField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

# Signals for handling cascaded deletions from Allauth models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

@receiver(post_delete, sender=EmailAddress)
def delete_user_on_email_delete(sender, instance, **kwargs):
    """
    If an EmailAddress is deleted from the admin panel, delete the associated User 
    if they have no other email addresses left. This matches the intuition that 
    deleting a user's primary/only email address deletes the user account.
    """
    user = instance.user
    if user and user.pk:
        User = get_user_model()
        if User.objects.filter(pk=user.pk).exists():
            if not EmailAddress.objects.filter(user=user).exists():
                user.delete()
