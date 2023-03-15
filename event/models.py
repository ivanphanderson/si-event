from django.db import models
from pegawai.models import Pegawai
from account.models import Account

class Event(models.Model):
  creator    = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
  event_name = models.CharField(max_length=255)
  start_date = models.DateTimeField()
  end_date   = models.DateTimeField()
  expense    = models.IntegerField()
  tax        = models.DecimalField(max_digits=5, decimal_places=2)
  sk_file    = models.BinaryField(null=True)

class EventEmployee(models.Model):
  employee = models.ForeignKey(Pegawai, on_delete=models.CASCADE)
  event    = models.ForeignKey(Event, on_delete=models.CASCADE)