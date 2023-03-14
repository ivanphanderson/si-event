from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from account.models import Account, User
from django.contrib.messages import get_messages
from .views import forget_password, ubah_password, handle_otp
from .models import PasswordOTP
import environ

env = environ.Env()
environ.Env.read_env()


FORGET_PASSWORD_URL = '/forget-password'
FORGET_PASSWORD_URL_SUBMIT = '/forget-password/submit'
OTP_URL_SUBMIT = '/otp/submit/submit'
UBAH_PASSWORD_URL_SUBMIT = '/ubah-password/submit/submit'
UBAH_PASSWORD_URL_ASAL = '/ubah-password/asd'
FORGET_PASSWORD_HTML = 'forget_password.html'
HALAMAN_OTP_HTML = 'halaman_otp.html'
HALAMAN_UBAH_PASSWORD_HTML = 'halaman_ubah_password.html'
UNEXPECTED_HTML = 'unexpected.html'
UBAH_PASSWORD_URL_USERNAME = '/ubah-password/tesname2'
LOGGED_IN_UBAH_PASSWORD_URL = '/account/ubah-password/submit'
OTP_URL_LENGKAP_USERNAME = 'https://si-event.herokuapp.com/otp/tesname2'
UBAH_PASSWORD_URL_LENGKAP_USERNAME = 'https://si-event.herokuapp.com/ubah-password/tesname2'
UBAH_PASSWORD_URL_LENGKAP_SUBMIT = 'https://si-event.herokuapp.com/ubah-password/submit/submit'

PASSWORD_UNTUK_TEST = env('PASSWORD_UNTUK_TEST')
PASSWORD_UNTUK_TEST_GANTI = env('PASSWORD_UNTUK_TEST_GANTI')
PASSWORD_UNTUK_TEST_GANTI_BEDA = env('PASSWORD_UNTUK_TEST_GANTI_BEDA')

REVERSE_AUTH_LOGIN = 'authentication:login'
REVERSE_UBAH_PASSWORD = 'account:ubah_password'
REVERSE_HOME_HOME = 'home:home'
LOGIN_HTML = 'login.html'
USERNAME_ATAU_PW_SALAH = 'Username atau Password salah!'

class LoginLogoutTest(TestCase):
    '''Test Module for Authentication Login and Logout Test'''

    def setUp(self):
        '''Create object to test based on models'''
        self.client = Client()

        self.ADMIN_USERNAME = 'test_admin'
        self.ADMIN_PASSWORD = 'testadmin123'
        self.ADMIN_EMAIL = 'test.admin@gmail.com'

        self.USER_USERNAME = 'test_user'
        self.USER_PASSWORD = 'testuser123'
        self.USER_EMAIL = 'test.user@gmail.com'

        self.STAFF_KEUANGAN_USERNAME = 'test_sk'
        self.STAFF_KEUANGAN_PASSWORD = 'testsk123'
        self.STAFF_KEUANGAN_EMAIL = 'test.sk@gmail.com'
        
        user_admin = User.objects.create()
        user_admin.username = self.ADMIN_USERNAME
        user_admin.email = self.ADMIN_EMAIL
        user_admin.set_password(self.ADMIN_PASSWORD)
        admin_acc = Account(
            user = user_admin,
            username = self.ADMIN_USERNAME,
            email = self.ADMIN_EMAIL,
            role = 'Admin'
        )
        admin_acc.user.username = self.ADMIN_USERNAME
        admin_acc.save()
        user_admin.save()

        user_user = User.objects.create()
        user_user.username = self.USER_USERNAME
        user_user.email = self.USER_EMAIL
        user_user.set_password(self.USER_PASSWORD)
        user_acc = Account(
            user = user_user,
            username = self.USER_USERNAME,
            email = self.USER_EMAIL,
            role = 'User'
        )
        user_acc.user.username = self.USER_USERNAME
        user_acc.save()
        user_user.save()
        
        user_sk = User.objects.create()
        user_sk.username = self.STAFF_KEUANGAN_USERNAME
        user_sk.email = self.STAFF_KEUANGAN_EMAIL
        user_sk.set_password(self.STAFF_KEUANGAN_PASSWORD)
        sk_acc = Account(
            user = user_sk,
            username = self.STAFF_KEUANGAN_USERNAME,
            email = self.STAFF_KEUANGAN_EMAIL,
            role = 'Staff Keuangan'
        )
        sk_acc.user.username = self.STAFF_KEUANGAN_USERNAME
        sk_acc.save()
        user_sk.save()

    def test_login_admin_success(self):
        logged_in = self.client.login(username=self.ADMIN_USERNAME, password=self.ADMIN_PASSWORD)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.ADMIN_USERNAME, 'password':self.ADMIN_PASSWORD}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_UBAH_PASSWORD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)

    def test_login_admin_dua_kali_success_to_home(self):
        self.client.login(username=self.ADMIN_USERNAME, password=self.ADMIN_PASSWORD)
        self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.ADMIN_USERNAME, 'password':self.ADMIN_PASSWORD}, follow=True)


        data = {
            'current_password': self.ADMIN_PASSWORD,
            'new_password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        self.client.post(LOGGED_IN_UBAH_PASSWORD_URL, data)

        self.client.logout()

        logged_in = self.client.login(username=self.ADMIN_USERNAME, password=PASSWORD_UNTUK_TEST_GANTI)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.ADMIN_USERNAME, 'password':PASSWORD_UNTUK_TEST_GANTI}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_HOME_HOME))
    
    def test_login_admin_failed(self):
        url = reverse(REVERSE_AUTH_LOGIN)
        response = self.client.post(url, {'username':'admin_unregistered', 'password':'p4ssw0rdd'})
        self.assertFalse(response.context['user'].is_authenticated)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertEqual(messages[0], USERNAME_ATAU_PW_SALAH)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)             

    def test_login_user_success(self):
        logged_in = self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.USER_USERNAME, 'password':self.USER_PASSWORD}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_UBAH_PASSWORD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)

    def test_login_user_dua_kali_success_to_home(self):
        self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)
        self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.USER_USERNAME, 'password':self.USER_PASSWORD}, follow=True)

        data = {
            'current_password': self.USER_PASSWORD,
            'new_password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        self.client.post(LOGGED_IN_UBAH_PASSWORD_URL, data)

        self.client.logout()

        logged_in = self.client.login(username=self.USER_USERNAME, password=PASSWORD_UNTUK_TEST_GANTI)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.USER_USERNAME, 'password':PASSWORD_UNTUK_TEST_GANTI}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_HOME_HOME))

    def test_login_user_failed(self):
        url = reverse(REVERSE_AUTH_LOGIN)
        response = self.client.post(url, {'username':'user_unregistered', 'password':'p4ssw0rdd'})
        self.assertFalse(response.context['user'].is_authenticated)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertEqual(messages[0], USERNAME_ATAU_PW_SALAH)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)

    def test_login_sk_success(self):
        logged_in = self.client.login(username=self.STAFF_KEUANGAN_USERNAME, password=self.STAFF_KEUANGAN_PASSWORD)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.STAFF_KEUANGAN_USERNAME, 'password':self.STAFF_KEUANGAN_PASSWORD}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_UBAH_PASSWORD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)

    def test_login_sk_dua_kali_success_to_home(self):
        self.client.login(username=self.STAFF_KEUANGAN_USERNAME, password=self.STAFF_KEUANGAN_PASSWORD)
        self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.STAFF_KEUANGAN_USERNAME, 'password':self.STAFF_KEUANGAN_PASSWORD}, follow=True)

        data = {
            'current_password': self.STAFF_KEUANGAN_PASSWORD,
            'new_password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        self.client.post(LOGGED_IN_UBAH_PASSWORD_URL, data)

        self.client.logout()

        logged_in = self.client.login(username=self.STAFF_KEUANGAN_USERNAME, password=PASSWORD_UNTUK_TEST_GANTI)
        self.assertEqual(logged_in, True)
        response = self.client.post(reverse(REVERSE_AUTH_LOGIN), {'username':self.STAFF_KEUANGAN_USERNAME, 'password':PASSWORD_UNTUK_TEST_GANTI}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse(REVERSE_HOME_HOME))

    def test_login_sk_failed(self):
        url = reverse(REVERSE_AUTH_LOGIN)
        response = self.client.post(url, {'username':'sk_unregistered', 'password':'p4ssw0rdd'})
        self.assertFalse(response.context['user'].is_authenticated)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertEqual(messages[0], USERNAME_ATAU_PW_SALAH)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(LOGIN_HTML)

    def test_logout_success(self):
        self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)
        url = reverse('authentication:logout')
        response = self.client.get(url, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(REVERSE_AUTH_LOGIN))

    def test_logout_failed(self):
        url = reverse('authentication:logout')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse(REVERSE_AUTH_LOGIN))

class ModelTest(TestCase):
    
    def setUp(self):
        self.USERNAME = 'testname1'
        self.OTP = 12345678
        PasswordOTP.objects.create(
            username = self.USERNAME,
            OTP = self.OTP
        )
    
    def test_model_password_otp(self):
        password_otp = PasswordOTP.objects.get(username=self.USERNAME, OTP=self.OTP)
        self.assertEqual(password_otp.username, self.USERNAME)
        self.assertEqual(password_otp.OTP, self.OTP)
        self.assertEqual(password_otp.is_redeem, False) # False karena belum dipakai dimana-mana
        self.assertEqual(password_otp.is_changed, False) # False karena belum dipakai dimana-mana


class LupaPasswordTest(TestCase):
    def setUp(self):
        self.USERNAME = 'tesname2'
        self.PASSWORD = PASSWORD_UNTUK_TEST
        self.EMAIL = 'tes@gmail.com'
        user = User.objects.create()
        user.username = self.USERNAME
        user.set_password(self.PASSWORD)
        account = Account(
            user = user,
            username = self.USERNAME, 
            email = self.EMAIL,
            role = 'Admin'
        )
        account.user.username = self.USERNAME
        account.save()
        user.save()
        

    def test_forget_password_is_exist(self):
        response = Client().get(FORGET_PASSWORD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, FORGET_PASSWORD_HTML)

    def test_using_forget_password_func(self):
        response = resolve(FORGET_PASSWORD_URL)
        self.assertEqual(response.func, forget_password)

    def test_forget_password_post(self):        
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }

        response = Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        self.assertRedirects(response, f'/otp/{self.USERNAME}', status_code=302, target_status_code=200)

    def test_forget_password_post_invalid_form(self):
        data = {
            'username': self.USERNAME,
        }

        response = Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, FORGET_PASSWORD_HTML)

    def test_forget_password_post_invalid_data(self):
        data = {
            'username':self.USERNAME,
            'email': 'asdsa@gmail.com'
        }

        response = Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, FORGET_PASSWORD_HTML)


    def test_otp_get_is_exist(self):
        response = Client().get('/otp/tes')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_OTP_HTML)

    def test_otp_func(self):
        response = resolve('/otp/tes')
        self.assertEqual(response.func, handle_otp)

    def test_otp_post_is_functional(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }

        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        response = Client().post(OTP_URL_SUBMIT, data2)
        self.assertRedirects(response, UBAH_PASSWORD_URL_USERNAME, status_code=302, target_status_code=200)

    def test_otp_post_otp_salah(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }

        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)

        data2 = {
            'OTP': 000000,
            'username': self.USERNAME
        }

        response = Client().post(OTP_URL_SUBMIT, data2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_OTP_HTML)

    def test_otp_post_username_salah(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }

        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username= self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': 'abc'
        }

        response = Client().post(f'/otp/submit/submit', data2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_OTP_HTML)

    def test_otp_post_dua_kali_gagal(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }

        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        response = Client().post(OTP_URL_SUBMIT, data2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_OTP_HTML)

    def test_ubah_password_get_is_exist(self):
        response = Client().get(UBAH_PASSWORD_URL_ASAL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_ubah_password_post_is_exist(self):
        response = Client().post(UBAH_PASSWORD_URL_SUBMIT, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_using_ubah_password_func(self):
        response = resolve(UBAH_PASSWORD_URL_ASAL)
        self.assertEqual(response.func, ubah_password)

    def test_ubah_password_get_is_functional(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username = self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': OTP_URL_LENGKAP_USERNAME}
        response = Client().get(UBAH_PASSWORD_URL_USERNAME, {}, **headers)


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_UBAH_PASSWORD_HTML)

    def test_ubah_password_get_is_functional_http_referer_versi_submit_otp(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username = self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': 'https://si-event.herokuapp.com/otp/submit/submit'}
        response = Client().get(UBAH_PASSWORD_URL_USERNAME, {}, **headers)


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_UBAH_PASSWORD_HTML)

    def test_ubah_password_get_is_functional_http_referer_versi_submit_password(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username = self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': 'https://si-event.herokuapp.com/ubah-password/submit/submit'}
        response = Client().get(UBAH_PASSWORD_URL_USERNAME, {}, **headers)


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_UBAH_PASSWORD_HTML)

    def test_ubah_password_tanpa_otp_valid(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': OTP_URL_LENGKAP_USERNAME}

        # username OTP dengan yang di url beda sehingga tidak ada OTP yang valid
        response = Client().get(UBAH_PASSWORD_URL_ASAL, {}, **headers)


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)
    

    def test_ubah_password_http_referer_invalid(self):
        headers = {'HTTP_REFERER': 'https://si-event.herokuapp.com/login'}
        response = Client().get(f'/ubah-password/tes', {}, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_ubah_password_post_is_functional(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': UBAH_PASSWORD_URL_LENGKAP_USERNAME}

        data3 = {
            'username': self.USERNAME,
            'password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        response = Client().post(UBAH_PASSWORD_URL_SUBMIT, data3, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'berhasil_ubah_password.html')

        updated_user = User.objects.get(username=self.USERNAME)
        self.assertTrue(updated_user.check_password(PASSWORD_UNTUK_TEST_GANTI))

    def test_ubah_password_post_is_functional_http_referer_versi_submit(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': UBAH_PASSWORD_URL_LENGKAP_SUBMIT}

        data3 = {
            'username': self.USERNAME,
            'password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        response = Client().post(UBAH_PASSWORD_URL_SUBMIT, data3, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'berhasil_ubah_password.html')

        updated_user = User.objects.get(username=self.USERNAME)
        self.assertTrue(updated_user.check_password(PASSWORD_UNTUK_TEST_GANTI))

    def test_ubah_password_post_password_beda(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': UBAH_PASSWORD_URL_LENGKAP_USERNAME}

        data3 = {
            'username': self.USERNAME,
            'password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI_BEDA
        }
        response = Client().post(UBAH_PASSWORD_URL_SUBMIT, data3, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, HALAMAN_UBAH_PASSWORD_HTML)


    def test_ubah_password_post_username_asal(self):
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': UBAH_PASSWORD_URL_LENGKAP_USERNAME}

        data3 = {
            'username': 'asdasdaaa',
            'password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        response = Client().post(f'/ubah-password/submit/submit', data3, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)

    def test_ubah_password_post_http_referer_asal(self):        
        data = {
            'username': self.USERNAME,
            'email': self.EMAIL
        }
        Client().post(FORGET_PASSWORD_URL_SUBMIT, data)
        otp_obj = PasswordOTP.objects.get(username=self.USERNAME)
        otp = otp_obj.OTP

        data2 = {
            'OTP': otp,
            'username': self.USERNAME
        }

        Client().post(OTP_URL_SUBMIT, data2)

        headers = {'HTTP_REFERER': 'https://si-event.herokuapp.com/account'}

        data3 = {
            'username': self.USERNAME,
            'password': PASSWORD_UNTUK_TEST_GANTI,
            'confirmation_password': PASSWORD_UNTUK_TEST_GANTI
        }
        response = Client().post(UBAH_PASSWORD_URL_SUBMIT, data3, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, UNEXPECTED_HTML)
        
