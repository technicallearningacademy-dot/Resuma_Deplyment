import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

history = [{"role": "system", "content": "You are AI."}]
history.append({"role": "user", "content": "Huge payload: " + ("a" * 30000)})
try:
    print(client._generate_hf_chat(history, "Qwen/Qwen2.5-Coder-32B-Instruct"))
except Exception as e:
    import traceback
    traceback.print_exc()
