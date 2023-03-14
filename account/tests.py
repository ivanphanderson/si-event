from django.test import TestCase
from django.test import Client
from django.urls import resolve
from .views import read_akun, update_akun
from .models import Account, User
import environ

env = environ.Env()
environ.Env.read_env()

ACCOUNT_URL = '/account/'
GANTI_STATUS_AKUN_URL = '/account/ganti-status-akun'
UNEXPECTED_HTML = 'unexpected.html'
PASSWORD_UNTUK_TEST = env('PASSWORD_UNTUK_TEST')

def set_up_login(self, role):
    self.client = Client()
    USERNAME = 'tesname'
    PASSWORD = PASSWORD_UNTUK_TEST
    user: User = User.objects.create()
    user.username = USERNAME
    user.set_password(PASSWORD)
    account = Account(
        user = user,
        username = USERNAME, 
        email = 'tes@gmail.com',
        role = role
    )
    account.user.username=USERNAME
    user.save()
    account.save()

    login = self.client.login(username=USERNAME, password=PASSWORD)
    self.assertTrue(login)

def set_up_akun_dummy(self):
    self.USERNAME = 'tesname2'
    self.PASSWORD = PASSWORD_UNTUK_TEST
    self.EMAIL = 'tes@gmail.com'
    user: User = User.objects.create()
    user.username = self.USERNAME
    user.set_password(self.PASSWORD)
    account = Account(
        user = user,
        username = self.USERNAME, 
        email = self.EMAIL,
        role = 'Admin'
    )
    account.user.username = self.USERNAME
    user.save()
    account.save()

    self.user_dummy = user
    self.account_dummy = account

class AccountTidakLoginTest(TestCase):
    def test_read_akun_is_exist(self):
        response = Client().get(ACCOUNT_URL)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(response, f'/login?next=/account/', status_code=302, target_status_code=200)

    def test_using_read_akun_func(self):
        found = resolve(ACCOUNT_URL)
        self.assertEqual(found.func, read_akun)

    def test_update_akun_is_exist(self):
        response = Client().get('/account/update/1')
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(response, f'/login?next=/account/update/1', status_code=302, target_status_code=200)

    def test_using_update_akun_func(self):
        found = resolve('/account/update/1')
        self.assertEqual(found.func, update_akun)

    def test_ganti_status_akun_is_exist(self):
        response = Client().post(GANTI_STATUS_AKUN_URL)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(response, f'/login?next=/account/ganti-status-akun', status_code=302, target_status_code=200)



class AccountSudahLoginAdminTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, 'Admin')
        set_up_akun_dummy(self)

    def test_admin_read_akun_is_exist(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read_akun.html')

    def test_admin_update_akun_is_exist(self):
        response = self.client.get(f'/account/update/{self.account_dummy.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_akun.html')
        
    def test_admin_update_akun_id_ngasal(self):
        response = self.client.get(f'/account/update/3333')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_admin_update_akun_id_bukan_int(self):
        response = self.client.get(f'/account/update/aasdd')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_admin_update_akun_post_is_exist(self):
        data = {
            'id_akun': self.account_dummy.id,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertRedirects(response, ACCOUNT_URL, status_code=302, target_status_code=200)
        
        updated_account = Account.objects.get(user=self.user_dummy)
        self.assertEqual(updated_account.role, "User")

    def test_admin_update_akun_post_id_ngasal(self):
        data = {
            'id_akun': 3333,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_admin_update_akun_post_id_bukan_int(self):
        data = {
            'id_akun': 'aassdd',
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_admin_ganti_status_akun_is_exist(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': self.account_dummy.id})
        status_awal = self.user_dummy.is_active
        self.assertRedirects(response, ACCOUNT_URL, status_code=302, target_status_code=200)
        updated_akun = User.objects.get(username=self.USERNAME)
        status_updated = updated_akun.is_active
        self.assertEqual(status_updated, not status_awal)

    def test_admin_ganti_status_akun_id_ngasal(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 3333})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_admin_ganti_status_akun_id_bukan_int(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 'aasdd'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)


class AccountSudahLoginUserTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, 'User')
        set_up_akun_dummy(self)
        

    def test_user_read_akun_is_exist(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_update_akun_is_exist(self):
        response = self.client.get(f'/account/update/{self.account_dummy.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_update_akun_id_ngasal(self):
        response = self.client.get(f'/account/update/3333')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_update_akun_id_bukan_int(self):
        response = self.client.get(f'/account/update/aasdd')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_update_akun_post_tidak_bisa(self):
        data = {
            'id_akun': self.account_dummy.id,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)
        
        updated_account = Account.objects.get(user=self.user_dummy)
        self.assertEqual(updated_account.role, "Admin") # Tidak terupdate

    def test_user_update_akun_post_id_ngasal(self):
        data = {
            'id_akun': 3333,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_update_akun_id_post_bukan_int(self):
        data = {
            'id_akun': 'aassdd',
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)


    def test_user_ganti_status_akun_is_exist(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': self.account_dummy.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_ganti_status_akun_id_ngasal(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 3333})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_user_ganti_status_akun_id_bukan_int(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 'aassdd'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)


class AccountSudahLoginStaffKeuanganTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, 'Staff Keuangan')
        set_up_akun_dummy(self)


    def test_staff_keuangan_read_akun_is_exist(self):
        response = self.client.get(ACCOUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_update_akun_is_exist(self):
        data = {
            'id_akun': self.account_dummy.id,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_update_akun_id_ngasal(self):
        response = self.client.get(f'/account/update/3333')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_update_akun_id_bukan_int(self):
        response = self.client.get(f'/account/update/aasdd')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_update_akun_post_tidak_bisa(self):
        data = {
            'id_akun': self.account_dummy.id,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)
        
        updated_account = Account.objects.get(user = self.user_dummy)
        self.assertEqual(updated_account.role, "Admin") # Tidak terupdate

    def test_staff_keuangan_update_akun_post_id_ngasal(self):
        data = {
            'id_akun': 3333,
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_update_akun_post_id_bukan_int(self):
        data = {
            'id_akun': 'aassdd',
            'role': "User"
        }
        response = self.client.post(f'/account/update/submit/submit', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)


    def test_staff_keuangan_ganti_status_akun_is_exist(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': self.account_dummy.id})
        self.assertEqual(response.status_code, 200)

    def test_staff_keuangan_ganti_status_akun_id_ngasal(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 3333})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_staff_keuangan_ganti_status_akun_id_bukan_int(self):
        response = self.client.post(GANTI_STATUS_AKUN_URL, {'id_akun': 'aassdd'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)