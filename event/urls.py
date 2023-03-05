from django.urls import path
from .views import create_event

urlpatterns = [
    path('', create_event, name='create_event'),
]
