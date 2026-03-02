"""
Custom User model and Profile models for the AI Resume Builder.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


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
        help_text='Custom daily AI generation limit. 0 = use system default (5)'
    )
    login_count = models.PositiveIntegerField(default=0, help_text='Total number of logins')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

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
