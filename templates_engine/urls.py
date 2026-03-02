from django.urls import path
from . import views

urlpatterns = [
    path('preview/', views.preview_pdf, name='preview_pdf'),
]
