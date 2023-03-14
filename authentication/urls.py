from django.urls import path
from .views import login_user, forget_password, submit_forget_password, handle_otp, submit_otp, ubah_password, submit_ubah_password

app_name = 'authentication'

urlpatterns = [
    path('login', login_user, name='login'),
    path('forget-password', forget_password, name='forget_password'),
    path('forget-password/submit', submit_forget_password, name='submit_forget_password'),
    path('otp/<username>', handle_otp, name='handle_otp'),
    path('otp/submit/submit', submit_otp, name='submit_otp'),
    path('ubah-password/<username>', ubah_password, name='ubah_password'),
    path('ubah-password/submit/submit', submit_ubah_password, name='submit_ubah_password'),
]