from django.urls import path
from log.views import display_log

app_name = "log"

urlpatterns = [
    path("", display_log, name="display-log"),
]
