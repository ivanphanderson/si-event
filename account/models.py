from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    ROLE_CHOICES = [
        ('Admin','Admin'),
        ('User','User'),
        ('Staff Keuangan', 'Staff Keuangan')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    username = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)