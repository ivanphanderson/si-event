from django.urls import path
from .views import home, forbidden

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('forbidden/', forbidden, name='forbidden',)
]