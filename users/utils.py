import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailOTP

logger = logging.getLogger(__name__)

def send_otp_email(user):
    """Generates an OTP and sends it to the user's email."""
    try:
        otp = EmailOTP.generate_otp(user)
        subject = 'Your ResumeForge Verification Code'
        message = f'Hi {user.first_name or "there"},\n\nYour verification code is: {otp.code}\n\nThis code is valid for 15 minutes.\n\nThanks,\nThe ResumeForge Team'
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #6366f1; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">ResumeForge AI</h2>
            </div>
            <div style="padding: 30px; background-color: #ffffff;">
                <p style="font-size: 16px; color: #334155;">Hi {user.first_name or "there"},</p>
                <p style="font-size: 16px; color: #334155;">Please use the following 6-digit code to verify your email address:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="display: inline-block; padding: 15px 30px; background-color: #f1f5f9; color: #0f172a; font-size: 24px; font-weight: bold; letter-spacing: 4px; border-radius: 8px; border: 2px dashed #cbd5e1;">{otp.code}</span>
                </div>
                <p style="font-size: 14px; color: #64748b; text-align: center;">This code will expire in 15 minutes.</p>
                <p style="font-size: 16px; color: #334155;">If you did not request this, you can safely ignore this email.</p>
            </div>
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="font-size: 12px; color: #94a3b8; margin: 0;">&copy; {timezone.now().year} ResumeForge AI. All rights reserved.</p>
            </div>
        </div>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        return True
    except Exception as e:
        import traceback
        print(f"FAILED TO SEND OTP EXACT ERROR: {e}")
        traceback.print_exc()
        logger.error(f"Failed to send OTP to {user.email}: {e}")
        return False

def send_raw_otp_email(email, first_name, otp_code):
    """Sends an OTP to an email address without a User object (pre-registration)."""
    try:
        subject = 'Your ResumeForge Verification Code'
        name_str = first_name or "there"
        message = f'Hi {name_str},\n\nYour verification code is: {otp_code}\n\nThis code is valid for 15 minutes.\n\nThanks,\nThe ResumeForge Team'
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #6366f1; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">ResumeForge AI</h2>
            </div>
            <div style="padding: 30px; background-color: #ffffff;">
                <p style="font-size: 16px; color: #334155;">Hi {name_str},</p>
                <p style="font-size: 16px; color: #334155;">Please use the following 6-digit code to verify your email address:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="display: inline-block; padding: 15px 30px; background-color: #f1f5f9; color: #0f172a; font-size: 24px; font-weight: bold; letter-spacing: 4px; border-radius: 8px; border: 2px dashed #cbd5e1;">{otp_code}</span>
                </div>
                <p style="font-size: 14px; color: #64748b; text-align: center;">This code will expire in 15 minutes.</p>
                <p style="font-size: 16px; color: #334155;">If you did not request this, you can safely ignore this email.</p>
            </div>
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="font-size: 12px; color: #94a3b8; margin: 0;">&copy; {timezone.now().year} ResumeForge AI. All rights reserved.</p>
            </div>
        </div>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message
        )
        return True
    except Exception as e:
        import traceback
        print(f"FAILED TO SEND RAW OTP EXACT ERROR: {e}")
        traceback.print_exc()
        logger.error(f"Failed to send raw OTP to {email}: {e}")
        return False
