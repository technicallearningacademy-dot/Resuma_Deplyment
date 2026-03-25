import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Testing PDF extraction...")
try:
    res = client.extract_from_pdf("This is a test PDF text.")
    print("Success:")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
