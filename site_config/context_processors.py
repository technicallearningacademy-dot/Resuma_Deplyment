from django.conf import settings
from .models import SiteConfiguration

def theme_processor(request):
    """
    Injects the `app_theme` and `SITE_URL` variables into every template context.
    """
    try:
        config_theme = SiteConfiguration.load().default_theme
    except Exception:
        config_theme = 'theme-ocean'
    
    site_url = getattr(settings, 'SITE_URL', '')
    
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        theme = request.user.profile.app_theme
        if theme and theme != 'system':
            return {
                'app_theme': theme,
                'SITE_URL': site_url
            }
    
    return {
        'app_theme': config_theme,
        'SITE_URL': site_url
    }
