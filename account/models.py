from django.db import models
from django.contrib.auth.models import User
from auth_sso.models import SSOUIAccount

class NonSSOAccount(models.Model):
    ROLE_CHOICES = [
        ('Admin','Admin'),
        ('User','User'),
        ('Staff Keuangan', 'Staff Keuangan'),
        ('Guest','Guest')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    username = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_first_login = models.BooleanField(default=True)
    def __str__(self):
        return f'{self.username} - {self.role}'

class Account(models.Model):
    ROLE_CHOICES = [
        ('Admin','Admin'),
        ('User','User'),
        ('Staff Keuangan', 'Staff Keuangan'),
        ('Guest','Guest')
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('Non SSO UI', 'Non SSO UI'),
        ('SSO UI', 'SSO UI')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    accNonSSO = models.ForeignKey(NonSSOAccount, on_delete=models.SET_NULL, null=True, blank=True)
    accSSO = models.ForeignKey(SSOUIAccount, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    accountType = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='')
    def __str__(self):
        return f'{self.accountType} - {self.username}, {self.role}'

