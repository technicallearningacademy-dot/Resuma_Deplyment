from .models import SiteConfiguration

def theme_processor(request):
    """
    Injects the `app_theme` variable into every template context.
    If the user is logged in and has a theme, use that.
    Otherwise, use the global default set by the admin.
    """
    try:
        config_theme = SiteConfiguration.load().default_theme
    except Exception:
        config_theme = 'theme-ocean'
    
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        theme = request.user.profile.app_theme
        if theme and theme != 'system':
            return {'app_theme': theme}
    
    return {'app_theme': config_theme}
