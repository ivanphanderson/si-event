from django.test import TestCase
from account.tests import set_up_login, set_up_akun_dummy
from django.urls import reverse

URL = reverse("log:display-log")


class DisplayLogNotAuthenticatedTest(TestCase):
    def test_read_log_not_authenticated(self):
        response = self.client.get(URL)
        # karena belum login, diarahkan ke halaman login
        self.assertRedirects(
            response, f"/login?next=/log/", status_code=302, target_status_code=200
        )


class DisplayLogAdminTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "Admin")
        set_up_akun_dummy(self)

    def test_admin_read_akun_is_exist(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log.html")


class DisplayLogNonAdminTest(TestCase):
    def setUp(self) -> None:
        set_up_login(self, "User")
        set_up_akun_dummy(self)

    def test_permissions_to_access_read_pegawai_with_non_admin(self):
        response = self.client.get(URL)
        # user tidak dapat mengakses halaman pegawai, akan dialihkan ke halaman forbidden
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forbidden.html")
