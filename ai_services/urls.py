from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_resume_ai, name='ai_generate'),
    path('enhance/', views.enhance_text_ai, name='ai_enhance'),
    path('optimize/', views.optimize_keywords_ai, name='ai_optimize'),
    path('chat/', views.chat_with_ai, name='ai_chat'),               # Conversational chat mode
    path('extract-pdf/', views.extract_pdf_ai, name='ai_extract_pdf'),  # PDF upload & extraction
    path('fetch-history/<int:resume_id>/', views.fetch_chat_history, name='ai_fetch_history'),
]

