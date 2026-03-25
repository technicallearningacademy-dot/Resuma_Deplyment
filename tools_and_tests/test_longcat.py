import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Testing direct LongCat generation:")
try:
    res = client._generate_longcat("Hello LongCat, are you there?", 50)
    print("Success Output:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
