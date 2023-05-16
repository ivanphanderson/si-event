from django.db import models
from pegawai.models import Pegawai
from account.models import Account
from django.core.validators import MinValueValidator

NOT_VALIDATED_YET = 'Not validated yet'

class Event(models.Model):
    STATUS_CHOICES = [
        ('Validated','Validated'),
        (NOT_VALIDATED_YET,NOT_VALIDATED_YET),
        ('Waiting for validation','Waiting for validation'),
        ('Rejected','Rejected'),

    ]

    creator = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    event_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    expense = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    sk_file = models.BinaryField(null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=NOT_VALIDATED_YET)
    signed_file = models.FileField(upload_to='pdfs/', null=True, blank=True)
    rejection_reason = models.TextField(default='', blank=True, null=True)

class EventEmployee(models.Model):
    employee = models.ForeignKey(Pegawai, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    honor = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    pph = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    netto = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    role = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        self.netto = ((100 - int(self.pph)) / 100) * int(self.honor)
        super().save(*args, **kwargs)

class ValidationFile(models.Model):
    creator = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    surat_tugas = models.FileField(upload_to='pdfs/', null=True, blank=True)
