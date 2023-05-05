# Create your models here.
from django.db import models
from account.models import Account

class Log(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="log")
    date = models.DateField(auto_now_add=True, blank=True)
    timestamp = models.TimeField(auto_now_add=True, blank=True)
    action = models.CharField(max_length=150)
