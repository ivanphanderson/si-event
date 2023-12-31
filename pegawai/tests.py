from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Pegawai
from log.models import Log
from django.contrib.auth.models import User
from account.models import Account
from .views import SaveUpdatePegawai, UpdatePegawaiView
from account.tests import set_up_login, set_up_akun_dummy
from .handler import DataCleaner


DATA_PEGAWAI_CSV = "data pegawai.csv"
SAVE_PEGAWAI_URL = "pegawai:save_pegawai"
ADD_PEGAWAI_ERROR_HTML = "add_pegawai_error.html"
KARYAWAN1_EMAIL = "karyawan1@gmail.com"
KARYAWAN2_EMAIL = "karyawan2@gmail.com"
ALAMAT_KARYAWAN_JEMBER = "Jember Tenggara"
SAVE_UPDATE_PEGAWAI_URL = "pegawai:save_update_pegawai"
UPDATE_PEGAWAI_ERROR_HTML = "update_pegawai_error.html"
KARYAWAN_NAMA = "Karyawan 1"
KARYAWAN_NAMA2 = "Karyawan 2"
ALAMAT_KARYAWAN_KALIMANTAN = "Kalimantan Tenggara"
EMAIL_UNTUK_TEST = "test@gmail.com"
URL_PEGAWAI = "/pegawai/"
URL_ADD_PEGAWAI = "pegawai:add_pegawai"
URL_UPDATE_PEGAWAI = "pegawai:update_pegawai"
URL_CETAK_DATA_PEGAWAI = "pegawai:cetak_data_pegawai"
URL_FORBIDDEN_PAGE = "forbidden.html"
DATA_PEGAWAI = b"Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2\n,,,,,,"


class BaseTestCase(TestCase):
    def create_user(self):
        USERNAME = "user"
        PASSWORD = "123123123"
        user: User = User.objects.create()
        user.username = USERNAME
        user.set_password(PASSWORD)
        account = Account(
            user=user, username=USERNAME, email=EMAIL_UNTUK_TEST, role="User"
        )
        account.user.username = USERNAME
        user.save()
        account.save()

    def setUp(self):
        self.client = Client()
        USERNAME = "tesname"
        PASSWORD = "123123123"
        user: User = User.objects.create()
        user.username = USERNAME
        user.set_password(PASSWORD)
        account = Account(
            user=user, username=USERNAME, email=EMAIL_UNTUK_TEST, role="Admin"
        )
        account.user.username = USERNAME
        user.save()
        account.save()

        self.create_user()

        login = self.client.login(username=USERNAME, password=PASSWORD)
        self.assertTrue(login)


class AddPegawaiTest(BaseTestCase):
    def test_add_pegawai_return_correct_template(self):
        response = self.client.get(reverse(URL_ADD_PEGAWAI))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_pegawai.html")

    def test_add_pegawai_pegawai_already_available_get_redirected(self):
        Pegawai.objects.create(
            email="emailtest@gmail.com",
            employee_no="196709052014091003",
            employee_name="pegawai redirected",
            employment_status="PNS",
            nama_di_rekening="pegawai redirected",
            nama_bank="bank tes123",
            nomor_rekening="1255552342312",
            nomor_npwp="2288382222333",
            alamat_npwp="alamat redirected uji",
        )
        response = self.client.get(reverse(URL_ADD_PEGAWAI))
        self.assertEqual(response.status_code, 302)

    def test_add_pegawai_not_logged_in_no_template(self):
        self.client.logout()
        response = self.client.get(reverse(URL_ADD_PEGAWAI))
        self.assertEqual(response.status_code, 302)

    def test_download_data_pegawai(self):
        Pegawai.objects.create(
            email="pegawaiujicetak@gmail.com",
            employee_no="1967090435345345343",
            employee_name="pegawai uji cetak data",
            employment_status="PNS",
            nama_di_rekening="pegawai uji cetak data",
            nama_bank="bank uji cetak data",
            nomor_rekening="12558843433",
            nomor_npwp="26666622333",
            alamat_npwp="alamat uji cetak data",
        )
        response = self.client.post(reverse(URL_CETAK_DATA_PEGAWAI))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Dispotition"], "attachment; filename=data_pegawai.xlsx"
        )

    def test_add_pegawai_not_authorized(self):
        self.client.logout()
        self.client.login(username="user", password="123123123")
        response = self.client.get(reverse(URL_ADD_PEGAWAI))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, URL_FORBIDDEN_PAGE)

    def test_add_pegawai_valid(self):
        data_pegawai = b"Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN1_EMAIL).exists())
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN2_EMAIL).exists())
        self.assertEqual(len(Log.objects.all()), 1)
        self.assertTrue(Log.objects.filter(action="Add Data Pegawai").first())

    def test_add_pegawai_with_trailing_empty_line(self):
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, DATA_PEGAWAI)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN1_EMAIL).exists())
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN2_EMAIL).exists())

    def test_add_pegawai_duplicate_email(self):
        data_pegawai = b"Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_add_pegawai_empty(self):
        data_pegawai = b""
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_add_pegawai_flipped_header_name(self):
        data_pegawai = b"Employee Information\nNo,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_add_pegawai_invalid_header(self):
        data_pegawai = b"Employee Information\n,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)


class ReadPegawaiNotAuthenticatedTest(TestCase):
    def test_read_log_not_authenticated(self):
        response = self.client.get(URL_PEGAWAI)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(
            response, f"/login?next=/pegawai/", status_code=302, target_status_code=200
        )


class ReadPegawaiTestAdmin(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "Admin")
        set_up_akun_dummy(self)

    def test_display_pegawai_template_empty_with_admin(self):
        response = self.client.get(URL_PEGAWAI)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "display_pegawai.html")

    def test_display_pegawai_template_not_empty(self):
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, DATA_PEGAWAI)
        self.client.post(reverse(SAVE_PEGAWAI_URL), {"file": file_data_pegawai})
        response = self.client.get(URL_PEGAWAI)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "display_pegawai.html")
        self.assertEqual(len(Pegawai.objects.all()), 2)


class ReadPegawaiNonAdminTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "User")
        set_up_akun_dummy(self)

    def test_permissions_to_access_read_pegawai_with_non_admin(self):
        response = self.client.get(URL_PEGAWAI)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, URL_FORBIDDEN_PAGE)


class UpdatePegawaiTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def setUpPegawaiDb(self):
        self.pegawai1 = Pegawai.objects.create(
            email=KARYAWAN1_EMAIL,
            employee_no="123",
            employee_name=KARYAWAN_NAMA,
            employee_category=Pegawai.STAFF,
            job_status=Pegawai.ADMINISTRASI,
            grade_level="I/b",
            employment_status="PNS",
            nama_di_rekening="sidfi",
            nama_bank="BANK NEGARA INDONESIA",
            nomor_rekening="1234534216",
            nomor_npwp="12345678941312",
            alamat_npwp=ALAMAT_KARYAWAN_JEMBER,
            tombstone=False,
        )
        self.pegawai2 = Pegawai.objects.create(
            email=KARYAWAN2_EMAIL,
            employee_no="234",
            employee_name=KARYAWAN_NAMA2,
            employee_category=Pegawai.LECTURER,
            job_status=Pegawai.DOSEN,
            grade_level="II/b",
            employment_status="PNS",
            nama_di_rekening="sidfiadsasdg",
            nama_bank="BANK NEGARA INDONESIA",
            nomor_rekening="12345342165531",
            nomor_npwp="123456789411234312",
            alamat_npwp=ALAMAT_KARYAWAN_KALIMANTAN,
            tombstone=False,
        )

    # Views-related tests
    def test_update_pegawai_return_correct_template(self):
        self.setUpPegawaiDb()
        response = self.client.get(reverse(URL_UPDATE_PEGAWAI))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_pegawai.html")

    def test_update_pegawai_pegawai_not_available_get_redirected(self):
        Pegawai.objects.filter(employee_no="123").delete()
        Pegawai.objects.filter(employee_no="234").delete()

        response = self.client.get(reverse(URL_UPDATE_PEGAWAI))

        self.assertEqual(response.status_code, 302)

    def test_update_pegawai_not_logged_in_no_template(self):
        self.client.logout()
        response = self.client.get(reverse(URL_UPDATE_PEGAWAI))
        self.assertEqual(response.status_code, 302)

    def test_update_pegawai_not_authorized(self):
        self.setUpPegawaiDb()
        self.client.logout()
        self.client.login(username="user", password="123123123")
        response = self.client.get(reverse(URL_UPDATE_PEGAWAI))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, URL_FORBIDDEN_PAGE)

    def test_update_pegawai_valid(self):
        data_pegawai = b"Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN1_EMAIL).exists())
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN2_EMAIL).exists())

    def test_update_pegawai_with_trailing_empty_line(self):
        """
        Make sure all Pegawai data is added even when there is trailing empty line in uploaded file
        """
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, DATA_PEGAWAI)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN1_EMAIL).exists())
        self.assertTrue(Pegawai.objects.filter(email=KARYAWAN2_EMAIL).exists())

    def test_update_pegawai_duplicate_email(self):
        """
        Make sure that all employee's email to be added are unique
        """
        data_pegawai = b"Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, UPDATE_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_update_pegawai_empty(self):
        """
        Make sure system handle empty file with correct status code and nothing changed in database
        """
        data_pegawai = b""
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, UPDATE_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_update_pegawai_flipped_header_name(self):
        """
        Make sure that no pegawai is added when the column name is wrong
        """
        data_pegawai = b"Employee Information\nNo,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, UPDATE_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_update_pegawai_invalid_header(self):
        """
        Make sure proper response is returned when the header is invalid
        """
        data_pegawai = b"Employee Information\n,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2"
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(
            reverse(SAVE_UPDATE_PEGAWAI_URL), {"file": file_data_pegawai}
        )

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, UPDATE_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_update_employee_category_is_correct_lecturer(self):
        """
        Make sure employee category is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.pegawai1.save()
        self.view.update_employee_category(self.pegawai1, "Lecturer")

        self.assertEqual(self.pegawai1.employee_category, Pegawai.LECTURER)

    def test_update_employee_category_is_correct_staff(self):
        """
        Make sure employee category is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.pegawai1.save()
        self.view.update_employee_category(self.pegawai1, "Staff")

        self.assertEqual(self.pegawai1.employee_category, Pegawai.STAFF)

    def test_update_employee_category_is_other(self):
        """
        Make sure employee category is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.view.update_employee_category(self.pegawai1, "Other")
        self.pegawai1.save()

        self.assertEqual(self.pegawai1.employee_category, Pegawai.STAFF)

    def test_update_employee_category_is_not_correct(self):
        """
        Make sure employee category is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.view.update_employee_category(self.pegawai1, "Lecturer")
        self.pegawai1.save()

        self.assertNotEqual(self.pegawai1.employee_category, Pegawai.STAFF)

    def test_update_job_status_is_correct(self):
        """
        Make sure job status is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.view.update_job_status(self.pegawai1, "Dosen")
        self.pegawai1.save()

        self.assertEqual(self.pegawai1.job_status, Pegawai.DOSEN)

    def test_update_job_status_is_not_correct(self):
        """
        Make sure job status is return correctly
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.view.update_job_status(self.pegawai1, "Fungsional Tertentu")
        self.pegawai1.save()

        self.assertNotEqual(self.pegawai1.job_status, Pegawai.ADMINISTRASI)

    def test_update_job_status_is_not_in_category(self):
        """
        Make sure job status is return administrasi (default)
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        self.view.update_job_status(self.pegawai1, "Other")
        self.pegawai1.save()

        self.assertEqual(self.pegawai1.job_status, Pegawai.ADMINISTRASI)

    def test_set_of_emails_filled_correctly(self):
        """
        Make sure that set_of_emails filled by email from database
        """
        self.view = SaveUpdatePegawai()
        self.setUpPegawaiDb()
        data = [
            [
                "1",
                "123",
                KARYAWAN_NAMA,
                "Staff",
                "Administrasi",
                "I/b",
                "PNS",
                KARYAWAN1_EMAIL,
                "sidfi",
                "BANK NEGARA INDONESIA",
                "1234534216",
                "12345678941312",
                ALAMAT_KARYAWAN_JEMBER,
            ]
        ]

        self.view.emails(None, data, 0)

        set_of_emails = set()
        all_pegawais = Pegawai.objects.all()

        for pegawai in all_pegawais:
            set_of_emails.add(pegawai.email)

        for datum in data:
            set_of_emails.remove(datum[7])

        self.assertEqual(len(all_pegawais), 2)
        self.assertEqual(len(set_of_emails), 1)
        self.assertEqual(set_of_emails, {KARYAWAN2_EMAIL})

    def test_update_pegawai_functionality_handler(self):
        data = [
            [
                "1",
                "123",
                KARYAWAN_NAMA,
                "Staff",
                "Administrasi",
                "I/b",
                "PNS",
                KARYAWAN1_EMAIL,
                "sidfi",
                "BANK NEGARA INDONESIA",
                "1234534216",
                "12345678941312",
                ALAMAT_KARYAWAN_JEMBER,
            ]
        ]
        functionality_handler = DataCleaner(None)
        functionality_handler.functionality(data, {})

    def test_emails_set_tombstone(self):
        """
        Test that the method sets tombstone to True for Pegawai objects with emails that are not in the data set
        """
        pegawai1 = Pegawai.objects.create(email="pegawai1@test.com")
        pegawai2 = Pegawai.objects.create(email="pegawai2@test.com")
        pegawai3 = Pegawai.objects.create(email="pegawai3@test.com")

        data = [
            [
                1,
                "employee_no1",
                "employee_name1",
                "category1",
                "job_status1",
                "grade_level1",
                "employment_status1",
                "pegawai1@test.com",
                "nama_di_rekening1",
                "nama_bank1",
                "nomor_rekening1",
                "nomor_npwp1",
                "alamat_npwp1",
            ],
            [
                2,
                "employee_no2",
                "employee_name2",
                "category2",
                "job_status2",
                "grade_level2",
                "employment_status2",
                "pegawai2@test.com",
                "nama_di_rekening2",
                "nama_bank2",
                "nomor_rekening2",
                "nomor_npwp2",
                "alamat_npwp2",
            ],
        ]

        self.view = SaveUpdatePegawai()
        self.view.emails(request=None, data=data, index=0)

        pegawai1.refresh_from_db()
        pegawai2.refresh_from_db()
        pegawai3.refresh_from_db()
        self.assertFalse(pegawai1.tombstone)
        self.assertFalse(pegawai2.tombstone)
        self.assertTrue(pegawai3.tombstone)
