import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
from resumes.models import Resume, ResumeChatMessage
from django.contrib.auth import get_user_model

client = get_client()

user = get_user_model().objects.first()
resume = Resume.objects.filter(user=user).first()
history = resume.chat_messages.all().order_by('created_at')[:20] if resume else None

print("Testing chat_with_assistant...")
try:
    res = client.chat_with_assistant("change the background color to White of the Template", history)
    print("Success:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
