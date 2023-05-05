from django.db import models
from datetime import timedelta
from django.utils import timezone

def now_plus_10_minutes():
    return timezone.now() + timedelta(minutes=10)


class PasswordOTP(models.Model):
    username = models.CharField(max_length=150, default="")
    OTP = models.IntegerField()
    valid_until = models.DateTimeField(default=now_plus_10_minutes, blank=True)
    is_redeem = models.BooleanField(default=False)
    is_changed = models.BooleanField(default=False)
