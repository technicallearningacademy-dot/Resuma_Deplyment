import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Testing direct Ollama generator:")
try:
    res = client._generate_local("Hello")
    print("Success:", res)
except Exception as e:
    print("Caught final cascaded exception:", e)
