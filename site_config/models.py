from django.db import models

class SiteConfiguration(models.Model):
    """Singleton model for global site settings."""
    
    THEME_OCEAN = 'theme-ocean'
    THEME_PINK_3D = 'theme-pink-3d'
    THEME_VIOLET_3D = 'theme-violet-3d'
    
    THEME_CHOICES = [
        (THEME_OCEAN, 'Ocean Mesh (Default)'),
        (THEME_PINK_3D, 'Pink Horizon'),
        (THEME_VIOLET_3D, 'Deep Violet X'),
    ]

    default_theme = models.CharField(
        max_length=50,
        choices=THEME_CHOICES,
        default=THEME_OCEAN,
        help_text="Default theme for logged-out users (e.g., landing page)"
    )
    
    enable_pink_theme = models.BooleanField(
        default=True, 
        help_text="Allow users to select the Pink Horizon theme"
    )
    
    enable_violet_theme = models.BooleanField(
        default=True, 
        help_text="Allow users to select the Deep Violet X theme"
    )

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def save(self, *args, **kwargs):
        # Ensure there's only one instance
        self.pk = 1 
        super(SiteConfiguration, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Global Site Configuration"
