import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from ai_services.client import get_client

client = get_client()

print("Testing chat_resume_edit...")
from django.contrib.auth import get_user_model
user = get_user_model().objects.first()

try:
    res = client.chat_resume_edit(
        user_prompt="Generate my resume from the uploaded PDF.",
        profile_data=None,
        current_latex="\\documentclass{article}\n\\begin{document}\nTest\n\\end{document}",
        template_style="modern_ats_clean",
        chat_history_qs=[]
    )
    print("Success:", len(res))
except Exception as e:
    import traceback
    traceback.print_exc()
