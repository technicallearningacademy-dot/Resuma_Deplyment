import os
import sys
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from ai_services.views import generate_resume_ai
from resumes.models import Resume

User = get_user_model().objects.first()
resume = Resume.objects.filter(user=User).first()

pdf_data = {
    "extracted_data": {
        "first_name": "Test"
    }
}
custom_prompt = "Generate my resume from the uploaded PDF.\n\n[USER PROVIDED PDF DATA TO BUILD FROM]:\n" + json.dumps(pdf_data)

payload = {
    "resume_id": resume.id if resume else None,
    "template_style": "modern_ats_clean",
    "custom_prompt": custom_prompt,
    "current_latex": "\\documentclass{article}\n\\begin{document}\nTest\n\\end{document}",
    "fast_mode": False
}

rf = RequestFactory()
request = rf.post('/ai/generate/', data=json.dumps(payload), content_type='application/json')
request.user = User

print("Testing generate_resume_ai...")
try:
    response = generate_resume_ai(request)
    print("Status:", response.status_code)
    try:
        print("Content:", response.content.decode())
    except:
        pass
except Exception as e:
    import traceback
    traceback.print_exc()
