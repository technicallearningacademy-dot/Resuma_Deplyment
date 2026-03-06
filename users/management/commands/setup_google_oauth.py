"""
Management command to set up the Google Social Application in the database.
This is required for django-allauth Google OAuth to work.
Run: python manage.py setup_google_oauth
"""
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Seeds the Google OAuth Social Application into the database for django-allauth'

    def handle(self, *args, **kwargs):
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        client_id = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('google', {}).get('APP', {}).get('client_id', '')
        secret = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('google', {}).get('APP', {}).get('secret', '')

        if not client_id or not secret:
            self.stdout.write(self.style.ERROR('Google OAuth credentials not found in settings. Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in your .env file.'))
            return

        # Get or create the Site
        site, _ = Site.objects.get_or_create(id=settings.SITE_ID, defaults={
            'domain': 'localhost:8000',
            'name': 'AI Resume Builder'
        })
        
        # Ensure the site has the correct domain
        if site.domain not in ['localhost:8000', '127.0.0.1:8000']:
            site.domain = 'localhost:8000'
            site.name = 'AI Resume Builder'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Site to localhost:8000'))

        # Create or update the Google Social App
        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': secret,
            }
        )
        app.sites.add(site)

        if created:
            self.stdout.write(self.style.SUCCESS('Google Social Application created and linked to site successfully!'))
        else:
            self.stdout.write(self.style.SUCCESS('Google Social Application updated and linked to site successfully!'))
        
        self.stdout.write(self.style.SUCCESS(f'  Provider: google'))
        self.stdout.write(self.style.SUCCESS(f'  Client ID: {client_id[:30]}...'))
        self.stdout.write(self.style.SUCCESS(f'  Site: {site.domain}'))
        self.stdout.write(self.style.WARNING('\nNOTE: Make sure your Google Cloud Console has http://localhost:8000 in the Authorized redirect URIs.'))
