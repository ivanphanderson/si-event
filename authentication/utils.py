from .models import PasswordOTP
from django.core.mail import send_mail
from django.conf import settings
import secrets

MIN_OTP = 10000000
MAX_OTP = 99999999

def create_otp(username):
    OTP = secrets.choice(range(MIN_OTP, MAX_OTP))
    PasswordOTP.objects.create(username=username, OTP=OTP)
    return OTP

def send_forget_password_email(username, recipient_email):
    OTP = create_otp(username)
    subject = "Change Password SI-Event"
    message = f"This is your OTP code: {OTP}. Don't share it!"
    send_email(recipient_email, subject, message)


def send_email(recipient, subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
    )


def is_valid_referer_ubah_password_get(http_referer):
    parts = http_referer.split("/")
    return (
        (len(parts) == 5 and parts[-2] == "otp")
        or (len(parts) == 6 and "/".join(parts[-3:]) == "ubah-password/submit/submit")
        or (len(parts) == 6 and "/".join(parts[-3:]) == "otp/submit/submit")
    )


def is_valid_referer_ubah_password_post(http_referer):
    parts = http_referer.split("/")
    return (len(parts) == 5 and parts[-2] == "ubah-password") or (
        len(parts) == 6 and "/".join(parts[-3:]) == "ubah-password/submit/submit"
    )
