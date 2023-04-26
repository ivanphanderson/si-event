from django.contrib import admin
from .models import Account, NonSSOAccount

admin.site.register(Account)
admin.site.register(NonSSOAccount)