from django.urls import path
from .views import AddPegawaiView, SavePegawaiToDatabase, DisplayPegawaiView

app_name = 'pegawai'

urlpatterns = [
    path('', DisplayPegawaiView.as_view(), name='display_pegawai'),
    path('add/', AddPegawaiView.as_view(), name='add_pegawai'),
    path('save-pegawai/', SavePegawaiToDatabase.as_view(), name='save_pegawai'),
]