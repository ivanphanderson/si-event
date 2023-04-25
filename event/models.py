from django.db import models
from pegawai.models import Pegawai
from account.models import Account
from django.core.validators import MinValueValidator


class Event(models.Model):
    creator = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    event_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    expense = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    sk_file = models.BinaryField(null=True)


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
