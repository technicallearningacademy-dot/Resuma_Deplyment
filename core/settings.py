"""
Django settings for the AI Resume Builder.
"""
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
# In production, read from env; in dev allow all
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app']

# Base URL for sharing links (Gmail, WhatsApp, Copy Link)
SITE_URL = config('SITE_URL', default='')
if SITE_URL:
    # Ensure it's trusted for CSRF if it's an external URL
    if SITE_URL.startswith('http'):
        CSRF_TRUSTED_ORIGINS.append(SITE_URL)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# Application definition
# =============================================================================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Local apps
    'users.apps.UsersConfig',
    'resumes.apps.ResumesConfig',
    'ai_services.apps.AiServicesConfig',
    'templates_engine.apps.TemplatesEngineConfig',
    'site_config.apps.SiteConfigConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    # Custom monitoring middleware
    'users.middleware.BlockedUserMiddleware',   # ← Instantly blocks banned users
    'users.middleware.TrackLastIPMiddleware',   # ← Tracks user IP address
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'site_config.context_processors.theme_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# =============================================================================
# Database — Uses DATABASE_URL in production (Railway PostgreSQL),
#             falls back to SQLite for local development
# =============================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# =============================================================================
# Authentication
# =============================================================================
AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth configuration
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False

# =============================================================================
# Email Configuration
# =============================================================================
# For development, emails will be printed to the console.
# In production, configure SMTP settings (e.g. Gmail, SendGrid, etc.)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@resumeforge.ai')

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Google OAuth
# NOTE: Client ID and Secret are stored in the database via the SocialApp model.
# Run: python manage.py setup_google_oauth  to seed/update credentials.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# =============================================================================
# Password validation
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# Internationalization
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# Static & Media files
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# Default primary key field type
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# AI API Keys
# =============================================================================
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
HF_API_TOKEN = config('HF_API_TOKEN', default='')  # Optional: Hugging Face (works without token too)
GROQ_API_KEY = config('GROQ_API_KEY', default='')   # Optional: Groq Cloud (High performance fallback)
LONGCAT_API_KEY = config('LONGCAT_API_KEY', default='') # Optional: LongCat API (User recommended fallback)

# =============================================================================
# File upload settings
# =============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# =============================================================================
# Security (production overrides)
# =============================================================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# =============================================================================
# Jazzmin Admin Theme Settings
# =============================================================================
JAZZMIN_SETTINGS = {
    "site_title": "ResumeForge Admin",
    "site_header": "ResumeForge AI",
    "site_brand": "ResumeForge AI",
    "welcome_sign": "Welcome back to ResumeForge Core",
    "search_model": ["users.CustomUser", "resumes.Resume"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "topmenu_links": [
        {"name": "Dashboard",  "url": "/", "permissions": ["auth.view_user"]},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "users.CustomUser": "fas fa-user",
        "resumes.Resume": "fas fa-file-alt",
        "resumes.AIPromptLog": "fas fa-robot",
        "resumes.ResumeVersion": "fas fa-history",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}
