import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

models_to_test = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "microsoft/Phi-3-mini-4k-instruct"
]

prompt = "Hello, respond with yes."

with open('hf_results.txt', 'w') as out:
    for model in models_to_test:
        out.write(f"--- Testing {model} ---\n")
        try:
            res = client._generate_hf(prompt, model, max_tokens=10)
            out.write(f"SUCCESS! Output: {res}\n")
        except Exception as e:
            out.write(f"FAILED: {e}\n")
