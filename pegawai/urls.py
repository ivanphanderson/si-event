from django.urls import path
from .views import (
    AddPegawaiView,
    SavePegawaiToDatabase,
    DisplayPegawai,
    UpdatePegawaiView,
    SaveUpdatePegawai,
)


app_name = "pegawai"

urlpatterns = [
    path("", DisplayPegawai.as_view(), name="display_pegawai"),
    path("add/", AddPegawaiView.as_view(), name="add_pegawai"),
    path("save-pegawai/", SavePegawaiToDatabase.as_view(), name="save_pegawai"),
    path("update/", UpdatePegawaiView.as_view(), name="update_pegawai"),
    path(
        "save-update-pegawai/", SaveUpdatePegawai.as_view(), name="save_update_pegawai"
    ),
]
