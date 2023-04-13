from django.test import TestCase
from account.tests import set_up_login, set_up_akun_dummy
from event.models import Event, EventEmployee
from pegawai.models import Pegawai
from account.models import Account, User
from django.db.models import Q

URL= '/pembayaran/'
TEST_EMAIL = 'teststaff@gmail.com'
TEST_USERNAME = 'testuser'
TEST_PASS = 'teststaff123'


class DisplayPembayaranNotAuthenticatedTest(TestCase):

    def test_read_pembayaran_not_authenticated(self):
        response = self.client.get(URL)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(response, f'/login?next=/pembayaran/', status_code=302, target_status_code=200)

class DisplayPembayaranNonStaffTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, 'User')
        set_up_akun_dummy(self)

    def test_permissions_to_access_read_pembayaran_with_non_staff(self):
        response = self.client.get(URL)
        # user tidak dapat mengakses halaman pegawai, akan dialihkan ke halaman forbidden
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

class FilterHonorTest(TestCase):
    def setUp(self):
        self.event_name = 'Test Event'
        self.binary_data = b'some binary data'

        self.user = User.objects.create_user(
        username= TEST_USERNAME, 
        password=TEST_PASS, 
        email= TEST_EMAIL
        )

        self.account = Account.objects.create(
        user = self.user,
        username = TEST_USERNAME,
        email = TEST_EMAIL,
        role = 'Staff Keuangan',
        is_first_login = True
        )

        self.pegawai = Pegawai.objects.create(
        email = TEST_EMAIL,
        employee_no = '1234567890',
        employee_name = 'Test User',
        employee_category = 'Staff',
        job_status = 'Administrasi',
        grade_level = '-',
        employment_status = 'Kontrak',
        nama_di_rekening = 'Test User',
        nama_bank = 'Mandiri',
        nomor_rekening = '2222222222',
        nomor_npwp = '563780000',
        alamat_npwp = 'Jl. Tangguh IV No 17 Rt 10/02 Kelapa Gading Barat Jakarta Utara'
        )

        login = self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        self.assertTrue(login)

        self.event = Event.objects.create(
            creator=self.account,
            event_name=self.event_name,
            start_date='2023-01-27',
            end_date='2023-03-28',
            expense=10000000,
            sk_file=self.binary_data
            )
    
    def test_filter_is_exist(self):
        filter_date = {
            'publishDateMin': '2023-03-28',
            'publishDateMax': '2023-04-28',
            'pegawai': self.pegawai.employee_name,
            'event': self.event.event_name,
        }

        response = self.client.get(URL, data=filter_date)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'filter_form.html')
    
    def test_filter_is_not_exist(self):
        filter_date = {
            'publishDateMin': '2022-03-28',
            'publishDateMax': '2022-04-28',
            'pegawai': '',
            'event': '',
        }

        response = self.client.get(URL, data=filter_date)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'filter_form.html')
        e = Event.objects.filter(end_date__gte='2023-03-28') 
        date = Event.objects.filter(end_date__lte='2023-04-28')
        event_emp_date = EventEmployee.objects.filter(Q(event__in=e) | Q(event__in=date))
        self.assertEqual(len(event_emp_date), 0)
        

