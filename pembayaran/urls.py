from django.urls import path
from .views import filter_honor_view

app_name = 'pembayaran'

urlpatterns = [
    path('', filter_honor_view, name='filter_honor_view'),
]