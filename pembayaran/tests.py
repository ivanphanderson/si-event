from django.test import TestCase
from django.urls import reverse
from account.tests import set_up_login, set_up_akun_dummy
from event.models import Event, EventEmployee
from pegawai.models import Pegawai
from account.models import Account, User, NonSSOAccount
from django.db.models import Q
import json
from io import BytesIO
import pandas as pd

URL = "/pembayaran/"
DOWNLOAD_EXCEL_STD_URL = reverse(
    "pembayaran:download_as_excel", kwargs={"type": "standard"}
)
DOWNLOAD_EXCEL_BTRMEMO_URL = reverse(
    "pembayaran:download_as_excel", kwargs={"type": "btrmemo"}
)
TEST_EMAIL = "teststaff@gmail.com"
TEST_USERNAME = "testuser"
TEST_PASS = "teststaff123"
NAME = "Test User"


class DisplayPembayaranNotAuthenticatedTest(TestCase):
    def test_read_pembayaran_not_authenticated(self):
        response = self.client.get(URL)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(
            response,
            "/login?next=/pembayaran/",
            status_code=302,
            target_status_code=200,
        )


class DisplayPembayaranNonStaffTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "User")
        set_up_akun_dummy(self)

    def test_permissions_to_access_read_pembayaran_with_non_staff(self):
        response = self.client.get(URL)
        # user tidak dapat mengakses halaman pegawai, akan dialihkan ke halaman forbidden
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forbidden.html")


class FilterHonorTest(TestCase):
    def setUp(self):
        self.event_name = "Test Event"
        self.binary_data = b"some binary data"

        self.user = User.objects.create_user(
            username=TEST_USERNAME, password=TEST_PASS, email=TEST_EMAIL
        )

        nonSSO_account = NonSSOAccount(
            user = self.user,
            username = TEST_USERNAME, 
            email = TEST_EMAIL,
            role = "Staff Keuangan",
            is_first_login=True,

        )
        nonSSO_account.save()
        self.account = Account.objects.create(
            user = self.user,
            accNonSSO = nonSSO_account,
            username = TEST_USERNAME, 
            email = TEST_EMAIL,
            role = "Staff Keuangan",
            accountType = 'Non SSO UI'
        )

        self.pegawai = Pegawai.objects.create(
            email=TEST_EMAIL,
            employee_no="1234567890",
            employee_name=NAME,
            employee_category="Staff",
            job_status="Administrasi",
            grade_level="-",
            employment_status="Kontrak",
            nama_di_rekening=NAME,
            nama_bank="Mandiri",
            nomor_rekening="2222222222",
            nomor_npwp="563780000",
            alamat_npwp="Jl. Tangguh IV No 17 Rt 10/02 Kelapa Gading Barat Jakarta Utara",
        )

        login = self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        self.assertTrue(login)

        self.event = Event.objects.create(
            creator=self.account,
            event_name=self.event_name,
            start_date="2023-01-27",
            end_date="2023-03-28",
            expense=10000000,
            sk_file=self.binary_data,
        )

        EventEmployee.objects.create(
            employee=Pegawai.objects.get(employee_name=NAME),
            event=Event.objects.get(event_name=self.event_name),
            role="ketua",
        )

    def test_filter_is_exist(self):
        filter_date = {
            "publishDateMin": "2023-03-28",
            "publishDateMax": "2023-04-28",
            "pegawai": self.pegawai.employee_name,
            "event": self.event.event_name,
        }

        response = self.client.get(URL, data=filter_date)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "filter_form.html")

    def test_filter_is_not_exist(self):
        filter_date = {
            "publishDateMin": "2022-03-28",
            "publishDateMax": "2022-04-28",
            "pegawai": "",
            "event": "",
        }

        response = self.client.get(URL, data=filter_date)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "filter_form.html")
        e = Event.objects.filter(end_date__gte="2023-03-28")
        date = Event.objects.filter(end_date__lte="2023-04-28")
        event_emp_date = EventEmployee.objects.filter(
            Q(event__in=e) | Q(event__in=date)
        )
        self.assertEqual(len(event_emp_date), 1)


class DownloadExcelFromData(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "Staff Keuangan")
        set_up_akun_dummy(self)
        self.data_table = {
            "0": {
                "no": "No.",
                "nama karyawan": "Nama",
                "tugas": "Tugas",
                "bruto": "Bruto(Rp.)",
                "pph": "Pph (%)",
                "netto": "Netto (Rp.)",
                "nama di rekening": "Nama di rekening",
                "bank": "Bank",
                "nomor rekening": "No Rekening",
            },
            "1": {
                "no": "1.",
                "nama karyawan": "Karyawan 1",
                "tugas": "Narasumber",
                "bruto": "30000",
                "pph": "5",
                "netto": "20000",
                "nama di rekening": "Karyawan 1 Rekening",
                "bank": "Bank Test",
                "nomor rekening": "123456789",
            },
            "2": {
                "total": "TOTAL",
                "total bruto": "30000",
                "total pph": "5",
                "total netto": "20000",
            },
        }

    def test_non_post_std_method(self):
        response = self.client.get(DOWNLOAD_EXCEL_STD_URL)
        self.assertEqual(response.status_code, 405)

    def test_non_post_btr_method(self):
        response = self.client.get(DOWNLOAD_EXCEL_BTRMEMO_URL)
        self.assertEqual(response.status_code, 405)

    def test_download_std_excel(self):
        response = self.client.post(
            DOWNLOAD_EXCEL_STD_URL,
            json.dumps(self.data_table),
            content_type="application/json",
        )

        excel_file = BytesIO(response.content)
        excel_file_content = pd.read_excel(excel_file)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "filename=data pembayaran panitia event.xlsx",
            response["Content-Dispotition"],
        )
        self.assertEquals(excel_file_content.shape, (2, 9))

    def test_download_btrmemo_excel(self):
        response = self.client.post(
            DOWNLOAD_EXCEL_BTRMEMO_URL,
            json.dumps(self.data_table),
            content_type="application/json",
        )

        excel_file = pd.ExcelFile(BytesIO(response.content))
        memo = pd.read_excel(excel_file, "memo")
        data_pembayaran = pd.read_excel(excel_file, "daftar pembayaran")

        self.assertEqual(response.status_code, 200)
        self.assertIn("filename=BTR dan memo.xlsx", response["Content-Dispotition"])
        self.assertIn("MEMO", memo.to_string())
        self.assertIn("Daftar Pembayaran Honor", data_pembayaran.to_string())
