from django.urls import path
from example_app.views import name_list

app_name = 'example_app'

urlpatterns = [
    path('', name_list, name='index'),
]