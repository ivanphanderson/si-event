from django.db import models
from django.contrib.auth.models import User


class SSOUIAccount(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("User", "User"),
        ("Staff Keuangan", "Staff Keuangan"),
        ("Guest", "Guest"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    kode_identitas = models.CharField(primary_key=True, max_length=1024)
    nama = models.CharField(max_length=1024)
    kode_organisasi = models.CharField(max_length=100)
    username = models.CharField(max_length=1024, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} - {self.role}"
