from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Pegawai
from log.models import Log
from django.contrib.auth.models import User
from account.models import Account


DATA_PEGAWAI_CSV = 'data pegawai.csv'
SAVE_PEGAWAI_URL = 'pegawai:save_pegawai'
ADD_PEGAWAI_ERROR_HTML = 'add_pegawai_error.html'

class AddPegawaiTest(TestCase):

    def setUp(self):
        self.client = Client()
        USERNAME = 'tesname'
        PASSWORD = '123123123'
        user: User = User.objects.create()
        user.username = USERNAME
        user.set_password(PASSWORD)
        account = Account(
            user = user,
            username = USERNAME, 
            email = 'tes@gmail.com',
            role = 'Admin'
        )
        account.user.username=USERNAME
        user.save()
        account.save()

        login = self.client.login(username=USERNAME, password=PASSWORD)
        self.assertTrue(login)

    def test_add_pegawai_return_correct_template(self):
        """
        Make sure add pegawai return correct template
        """
        response = self.client.get(reverse("pegawai:add_pegawai"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_pegawai.html')

    def test_add_pegawai_valid(self):
        """
        Make sure all Pegawai data is added
        """
        data_pegawai = b'Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email='karyawan1@gmail.com').exists())
        self.assertTrue(Pegawai.objects.filter(email='karyawan2@gmail.com').exists())
        self.assertEqual(len(Log.objects.all()), 1)
        self.assertTrue(Log.objects.filter(action='Add Data Pegawai').first())

    def test_add_pegawai_with_trailing_empty_line(self):
        """
        Make sure all Pegawai data is added even when there is trailing empty line in uploaded file
        """
        data_pegawai = b'Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2\n,,,,,,'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(Pegawai.objects.all()), 2)
        self.assertTrue(Pegawai.objects.filter(email='karyawan1@gmail.com').exists())
        self.assertTrue(Pegawai.objects.filter(email='karyawan2@gmail.com').exists())

    def test_add_pegawai_duplicate_email(self):
        """
        Make sure that all employee's email to be added are unique
        """
        data_pegawai = b'Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)
    
    def test_add_pegawai_empty(self):
        """
        Make sure system handle empty file with correct status code and nothing changed in database
        """
        data_pegawai = b''
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_add_pegawai_flipped_header_name(self):
        """
        Make sure that no pegawai is added when the column name is wrong
        """
        data_pegawai = b'Employee Information\nNo,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

    def test_add_pegawai_invalid_header(self):
        """
        Make sure proper response is returned when the header is invalid
        """
        data_pegawai = b'Employee Information\n,Employee Name,Employee No.\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        response = self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, ADD_PEGAWAI_ERROR_HTML)
        self.assertEqual(len(Pegawai.objects.all()), 0)

class ReadPegawaiTest(TestCase):

    def test_display_pegawai_template_empty(self):
        response = self.client.get('/pegawai/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'display_pegawai.html')
        self.assertContains(response, '<h4 style="text-align: center;">Data Pegawai</h4>', status_code=200)

    def test_display_pegawai_template_not_empty(self):
        data_pegawai = b'Employee Information\nNo,Employee No.,Employee Name,\
            Employee Category,Job Status,Grade Level,Employment Status,Email,\
            NAMA DI REKENING,NAMA BANK,NO REKENING,Nomor NPWP,Alamat NPWP\n\
            1,196709052014091003,Karyawan 1,Staff,Administrasi,I/d,PNS,karyawan1@gmail.com,\
            Karyawan 1,Bank Negara Indonesia,1255555526,222222222222,Perum. Sesuatu 1\n\
            2,196709052014091088,Karyawan 2,Staff,Administrasi,I/d,PNS,karyawan2@gmail.com,\
            Karyawan 2,Bank Negara Indonesia,1255555528,222222222223,Perum. Sesuatu 2\n,,,,,,'
        file_data_pegawai = SimpleUploadedFile(DATA_PEGAWAI_CSV, data_pegawai)
        self.client.post(reverse(SAVE_PEGAWAI_URL), {'file': file_data_pegawai})
        response = self.client.get('/pegawai/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'display_pegawai.html')
        self.assertEqual(len(Pegawai.objects.all()), 2)
