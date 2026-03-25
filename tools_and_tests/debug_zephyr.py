import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

import fitz
try:
    with open('Software_Engineer.pdf', 'rb') as f:
        pdf_bytes = f.read()
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    raw_text = ""
    for page in doc:
        raw_text += page.get_text() + "\n"
    raw_text_trimmed = raw_text[:15000]
except Exception as e:
    raw_text_trimmed = "dummy text " * 1000

print(f"Text length: {len(raw_text_trimmed)}")

try:
    print("Testing Zephyr with max_tokens=4096...")
    res = client._generate_hf(raw_text_trimmed, "HuggingFaceH4/zephyr-7b-beta", max_tokens=4096)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
