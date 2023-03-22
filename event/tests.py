from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from django.utils import timezone
import datetime

from .models import Event, EventEmployee
from pegawai.models import Pegawai
from account.models import Account
from django.contrib.auth.models import User
from log.models import Log

class EventModelTest(TestCase):

  def setUp(self):
    email = 'joni@gmail.com'

    self.event_name = 'Test Event'
    self.binary_data = b'some binary data'

    self.user = User.objects.create_user(
      username='admin', 
      password='admin123', 
      email='adminkece@gmail.com'
    )

    self.account = Account.objects.create(
      user = self.user,
      username = 'jonikeren',
      email = email,
      role = 'User',
      is_first_login = True
    )

    self.pegawai = Pegawai.objects.create(
      email = email,
      employee_no = 'employee1',
      employee_name = 'Jonyy',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '247128658',
      alamat_npwp = 'Jl. Hj. Halimah Saeran I No. 1 RT. 004/02 Kukusan Beji Depok'
    )

    login = self.client.login(username='admin', password='admin123')
    self.assertTrue(login)

  def test_create_event(self):
    event = Event.objects.create(
      creator=self.account,
      event_name=self.event_name,
      start_date=timezone.now(),
      end_date=timezone.now() + timezone.timedelta(days=1),
      expense=100000,
      tax=10.0,
      sk_file=self.binary_data
    )
    self.assertIsInstance(event, Event)
    self.assertEqual(event.creator, self.account)
    self.assertEqual(event.event_name, self.event_name)
    self.assertLess(event.start_date, event.end_date)
    self.assertEqual(event.expense, 100000)
    self.assertEqual(event.tax, 10.0)
    self.assertEqual(event.sk_file, self.binary_data)
    
  def test_create_event_will_add_log(self):
    data = {
      'creator':self.account,
      'event_name':self.event_name,
      'start_date':timezone.now(),
      'end_date':timezone.now() + timezone.timedelta(days=1),
      'expense':100000,
      'tax':10.0,
      'sk_file':self.binary_data
    }
    self.client.post(reverse('create_event'), data)
    self.assertEqual(len(Log.objects.all()), 1)
    action = 'Create ' + self.event_name + ' event'
    self.assertTrue(Log.objects.filter(action=action).first())

  def test_create_event_employee(self):
    event = Event.objects.create(
      creator=self.account,
      event_name=self.event_name,
      start_date=timezone.now(),
      end_date=timezone.now() + timezone.timedelta(days=1),
      expense=100000,
      tax=10.0,
      sk_file=self.binary_data
    )

    event_employee = EventEmployee.objects.create(
      employee=self.pegawai,
      event=event
    )

    self.assertIsInstance(event_employee, EventEmployee)
    self.assertEqual(event_employee.employee, self.pegawai)
    self.assertEqual(event_employee.event, event)


class CreateEventViewTestCase(TestCase):
    def setUp(self):
      self.event_name = 'Test Event'
      self.client = Client()
      self.user = User.objects.create_user(username='testuser', password='testpass')
      self.account = Account.objects.create(
        user = self.user,
        username = 'jonikeren',
        email = 'johndoe@gmail.com',
        role = 'User',
        is_first_login = True
      )
      self.pegawai = Pegawai.objects.create(
        email = 'johndoe@gmail.com',
        employee_no = 'employee1',
        employee_name = 'Jonyy',
        employee_category = 'Staff',
        job_status = 'Administrasi',
        grade_level = '-',
        employment_status = 'Kontrak',
        nama_di_rekening = 'karyawankeren',
        nama_bank = 'Mandiri',
        nomor_rekening = '4971335367',
        nomor_npwp = '247128658',
        alamat_npwp = 'Jl. Hj. Halimah Saeran I No. 1 RT. 004/02 Kukusan Beji Depok'
      )
      self.file = SimpleUploadedFile('pegawai.csv', b'No,nama,nomor pegawai\n1,Jonyy,employee1')
      self.client.login(username='testuser', password='testpass')

      self.start_date = '2023-03-20 23:00:00'
      self.end_date   = '2023-03-22 23:45:23'
      self.strpformat = '%Y-%m-%d %H:%M:%S'
    
    def test_create_event_get(self):
      response = self.client.get(reverse('create_event'))
      self.assertEqual(response.status_code, 200)

    def test_create_event_with_file_upload(self):
      url = reverse('create_event')

      start_dt_obj = datetime.datetime.strptime(self.start_date, self.strpformat)
      end_dt_obj = datetime.datetime.strptime(self.end_date, self.strpformat)

      data = {
          'event_name': self.event_name,
          'start_date': self.start_date,
          'end_date': self.end_date,
          'expense': 5000,
          'tax': 500,
          'pegawai_file': self.file,
      }
      response = self.client.post(url, data, follow=True)
      self.assertEqual(response.status_code, 200)

      event = Event.objects.last()
      event_employee = EventEmployee.objects.last()
      self.assertEqual(Event.objects.count(), 1)
      self.assertEqual(event.creator, self.account)
      self.assertEqual(event.event_name, self.event_name)
      self.assertEqual(event.start_date, start_dt_obj.replace(tzinfo=datetime.timezone.utc))
      self.assertEqual(event.end_date, end_dt_obj.replace(tzinfo=datetime.timezone.utc))
      self.assertEqual(event.expense, 5000)
      self.assertEqual(event.tax, 500)
      self.assertEqual(event_employee.employee, self.pegawai)
      self.assertEqual(event_employee.event, event)

    def test_create_event_with_email_list(self):
      url = reverse('create_event')

      start_dt_obj = datetime.datetime.strptime(self.start_date, self.strpformat)
      end_dt_obj = datetime.datetime.strptime(self.end_date, self.strpformat)

      data = {
          'event_name': self.event_name,
          'start_date': '2023-03-20 23:00:00',
          'end_date': '2023-03-22 23:45:23',
          'expense': 6000,
          'tax': 600,
          'pegawai_file': self.file,
          'list_employee_no': 'employee1',
      }
      response = self.client.post(url, data, follow=True)
      self.assertEqual(response.status_code, 200)

      event = Event.objects.last()
      event_employee = EventEmployee.objects.last()
      self.assertEqual(event.creator, self.account)
      self.assertEqual(Event.objects.count(), 1)
      self.assertEqual(event.event_name, self.event_name)
      self.assertEqual(event.start_date, start_dt_obj.replace(tzinfo=datetime.timezone.utc))
      self.assertEqual(event.end_date, end_dt_obj.replace(tzinfo=datetime.timezone.utc))
      self.assertEqual(event.expense, 6000)
      self.assertEqual(event.tax, 600)
      self.assertEqual(event_employee.employee, self.pegawai)
      self.assertEqual(event_employee.event, event)
  
class CreateUnauthorizedEventViewTestCase(TestCase):
    def test_unauthenticated_create(self):
      response = self.client.get(reverse('create_event'))
      self.assertEqual(response.status_code, 302)
