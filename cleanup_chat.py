import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import ResumeChatMessage

User = get_user_model()

# 1. Clear any custom api_daily_limit that is restricting users
for u in User.objects.all():
    if hasattr(u, 'api_daily_limit') and u.api_daily_limit is not None and u.api_daily_limit != 0:
        print(f"Resetting limit for {str(u)} from {u.api_daily_limit} to 0 (Default 50)")
        u.api_daily_limit = 0
        u.save()

# 2. Delete corrupted chat messages containing raw HTML 
corrupted_msgs = ResumeChatMessage.objects.filter(content__contains='<button onclick="generateWithAI()"')
count = corrupted_msgs.count()
corrupted_msgs.delete()
print(f"Deleted {count} corrupted chat messages containing raw HTML buttons.")
