import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

print("Testing large HF payload...")
try:
    huge_text = "LaTeX content " * 1000
    res = client._generate_hf(huge_text, "Qwen/Qwen2.5-Coder-32B-Instruct", 500)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
