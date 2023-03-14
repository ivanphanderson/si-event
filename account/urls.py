from django.urls import path
from .views import register_account, read_akun, update_akun, submit_update_akun, ganti_status_akun

app_name = 'account'

urlpatterns = [
    path('register', register_account, name='registerAccount'),
    path('', read_akun, name='read_akun'),
    path('update/<id>', update_akun, name='update_akun'),
    path('update/submit/submit', submit_update_akun, name='update_akun'),
    path('ganti-status-akun', ganti_status_akun, name='deactivate_akun')
]
