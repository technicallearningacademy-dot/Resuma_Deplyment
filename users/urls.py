from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/upload-photo-ajax/', views.upload_photo_ajax, name='upload_photo_ajax'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('verify-email/', views.verify_email_otp, name='verify_email_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('account-suspended/', views.account_suspended, name='account_suspended'),
]
