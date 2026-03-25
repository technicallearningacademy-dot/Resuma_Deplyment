import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()
print("Testing HF text_generation directly...")
try:
    res = client._generate_hf("Return the word hello.", "Qwen/Qwen2.5-Coder-32B-Instruct", 100)
    print("Success:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
