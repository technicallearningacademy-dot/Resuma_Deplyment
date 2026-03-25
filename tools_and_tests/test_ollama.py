import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Testing the full fallback chain (expecting Ollama localized error message if not running):")
try:
    # We force the fallback to trigger by giving an incredibly large prompt that HF rejects
    res = client.generate("Trigger local fallback by doing nothing.")
    print("Success:", res)
except Exception as e:
    print("Caught final cascaded exception:", e)
