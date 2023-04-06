from django.urls import path
from .views import create_event, input_employee_to_event, get_options, get_events

urlpatterns = [
    path('', get_events, name='get_events'),
    path('create', create_event, name='create_event'),
    path('input_employee', input_employee_to_event, name='input_employee_to_event'),
    path('get-options/', get_options, name='get_options'),
]
