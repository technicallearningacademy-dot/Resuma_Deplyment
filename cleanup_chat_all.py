import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from resumes.models import ResumeChatMessage

count = ResumeChatMessage.objects.all().count()
ResumeChatMessage.objects.all().delete()
print(f"Deleted ALL {count} chat messages to ensure a clean state.")
