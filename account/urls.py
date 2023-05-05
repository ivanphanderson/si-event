from django.urls import path
from .views import (
    register_account,
    read_akun,
    update_akun,
    submit_update_akun,
    ganti_status_akun,
    ubah_password,
    submit_ubah_password,
)

app_name = "account"

urlpatterns = [
    path("register", register_account, name="registerAccount"),
    path("", read_akun, name="read_akun"),
    path("update/<id>", update_akun, name="update_akun"),
    path("update/submit/submit", submit_update_akun, name="update_akun"),
    path("ganti-status-akun", ganti_status_akun, name="deactivate_akun"),
    path("ubah-password", ubah_password, name="ubah_password"),
    path("ubah-password/submit", submit_ubah_password, name="submit_ubah_password"),
]
