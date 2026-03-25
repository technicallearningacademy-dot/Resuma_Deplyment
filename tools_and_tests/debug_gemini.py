import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_services.client import get_client
client = get_client()

from ai_services.prompts import get_chat_edit_system_prompt
import google.generativeai as genai

system_instruction, _ = get_chat_edit_system_prompt(None, "modern_ats_clean")

try:
    print("Testing direct Gemini call...")
    custom_model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=system_instruction)
    chat = custom_model.start_chat(history=[])
    response = chat.send_message("Test message")
    print("Gemini Success! Response length:", len(response.text))
except Exception as e:
    print("GEMINI CRASHED WITH:")
    import traceback
    traceback.print_exc()
