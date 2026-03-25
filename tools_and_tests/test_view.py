import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from ai_services.views import extract_pdf_ai
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
user = User.objects.first()

rf = RequestFactory()
with open('test_api.pdf', 'rb') as f:
    pdf_content = f.read()
pdf = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
request = rf.post('/ai/extract-pdf/', {'pdf_file': pdf})
request.user = user

print("Testing extract_pdf_ai...")
try:
    response = extract_pdf_ai(request)
    print("Status:", response.status_code)
    print("Content:", response.content)
except Exception as e:
    import traceback
    traceback.print_exc()
