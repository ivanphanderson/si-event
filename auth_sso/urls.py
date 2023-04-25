from django.urls import path
from .views import login_sso

app_name = 'auth_sso'

urlpatterns = [
    path('login/', login_sso, name='login_sso'),
]
