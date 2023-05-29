from django.contrib import admin
from .models import Event, EventEmployee, ValidationFile

admin.site.register(Event)
admin.site.register(EventEmployee)
admin.site.register(ValidationFile)
