from django.urls import path
from .views import filter_honor_view, download_excel_from_data

app_name = "pembayaran"

urlpatterns = [
    path("", filter_honor_view, name="filter_honor_view"),
    path(
        "download-excel/<str:type>", download_excel_from_data, name="download_as_excel"
    ),
]
