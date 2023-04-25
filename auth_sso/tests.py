from django.test import TestCase, Client
from unittest.mock import patch, Mock
from .models import SSOUIAccount
from account.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from .utils import get_sso_ui_data

class LoginSSOTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('auth_sso:login_sso')
        self.username = 'rizky.juniastiar'
        self.password = 'passwordsso'
        
    @patch('auth_sso.views.get_sso_ui_data')
    def test_sso_successfully_login(self, mock_sso_data):
        mock_sso_data.return_value.json.return_value = { 
            "username": "rizky.juniastiar", 
            "nama": "Rizky Juniastiar", 
            "state": 1, 
            "kode_org": "09.00.12.01:mahasiswa", 
            "kodeidentitas": "2006596043", 
            "nama_role": "mahasiswa" 
        } 
        response = self.client.post(self.url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.url, '/home')
        self.assertEqual(response.status_code, 302)

        # Assert that a new SSOUIAccount and User were created
        self.assertEqual(SSOUIAccount.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        
        # Assert that the created user has the correct attributes
        user = User.objects.first()
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, f'{self.username}@ui.ac.id')
        
        # Assert that the SSOUIAccount was created with the correct attributes
        sso_account = SSOUIAccount.objects.first()
        self.assertEqual(sso_account.user, user)
        self.assertEqual(sso_account.kode_identitas, '2006596043')
        self.assertEqual(sso_account.nama, 'Rizky Juniastiar')
        self.assertEqual(sso_account.kode_organisasi, '09.00.12.01')
        self.assertEqual(sso_account.username, self.username)
        self.assertEqual(sso_account.role, 'Guest')

    @patch('auth_sso.views.get_sso_ui_data')
    def test_sso_invalid_credentials(self, mock_sso_data):
        mock_sso_data.return_value.json.return_value = {
            'state': 0
        }
        response = self.client.post(self.url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.url, self.url)
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertEqual(messages[0], 'Wrong SSO UI credentials')
        
        # Assert that no new SSOUIAccount or User were created
        self.assertEqual(SSOUIAccount.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)
    
    def test_get_login_sso_view(self):
        response = self.client.get(reverse('auth_sso:login_sso'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('login_sso.html')
        self.assertEqual(response.context['form'], 'form')

class TestGetSSOUIData(TestCase):
    
    @patch('auth_sso.utils.requests.post')
    def test_get_sso_ui_data(self, mock_post):
        # Set up the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'xyz123'}
        mock_post.return_value = mock_response
        
        # Call the function with some test data
        response = get_sso_ui_data('test_user', 'test_password')
        
        # Check that the mock was called with the correct arguments
        mock_post.assert_called_once_with(
            'https://api.cs.ui.ac.id/authentication/ldap/v2/',
            data = {
                'username': 'test_user',
                'password': 'test_password'
            }
        )
        
        # Check that the function returns the expected value
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'token': 'xyz123'})

class SSOUIAccountModelTestCase(TestCase):

    def test_sso_ui_account_str_representation(self):
        user = User.objects.create(username='rizky.juniastiar')
        account = SSOUIAccount.objects.create(
            user=user,
            kode_identitas='2006596043',
            nama='Rizky Juniastiar',
            kode_organisasi='09.00.12.01',
            username='rizky.juniastiar',
            role='Admin'
        )
        expected_str = f'{account.username} - {account.role}'
        self.assertEqual(str(account), expected_str)