import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Verifying full fallback chain (Gemini -> LongCat):")
try:
    # This should hit Gemini, fail, then hit LongCat successfully.
    res = client.generate("Please just say 'Fallback Success'.")
    print("\nResult:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
