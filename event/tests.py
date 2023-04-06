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

from django.core.exceptions import ValidationError
from .validators import validate_event_employee_fields

CREATE_EVENT = 'create_event.html'
EVENT_LIST = 'event_list.html'

class EventCreateViewTestCase(TestCase):
  def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(
        username='testuser', email='testuser@test.com', password='testpassword')
    self.client.login(username='testuser', password='testpassword')

    self.account = Account.objects.create(
      user = self.user,
      username = 'jonikeren',
      email = 'acc1@example.com',
      role = 'User',
      is_first_login = True
    )
    
    self.pegawai1 = Pegawai.objects.create(
      email = 'pegawai1@gmail.com',
      employee_no = '111',
      employee_name = 'joni',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '247128658',
      alamat_npwp = 'Jl. Hj. Hasannah Saeran I No. 1 RT. 004/02 Kukusan Beji Depok'
    )

    self.pegawai2 = Pegawai.objects.create(
      email = 'pegawai2@gmail.com',
      employee_no = '222',
      employee_name = 'jono',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '2471286667',
      alamat_npwp = 'Jl. Hj. Hasannah Saeran II No. 1 RT. 004/02 Kukusan Beji Depok'
    )

    self.start_date = '2023-03-21'
    self.end_date   = '2023-03-23'
    self.strpformat = '%Y-%m-%d'
  
  def test_create_event_get(self):
    response = self.client.get(reverse('create_event'))
    self.assertEqual(response.status_code, 200)

  def test_create_event_only(self):
    url = reverse('create_event')
    
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, CREATE_EVENT)

    new_event_name = 'Test Event_Baru'
    start_dt_obj = datetime.datetime.strptime(self.start_date, self.strpformat).date()
    end_dt_obj = datetime.datetime.strptime(self.end_date, self.strpformat).date()
    
    sess_data = {
      'event_name': new_event_name,
      'start_date': self.start_date,
      'end_date': self.end_date,
    }

    response = self.client.post(url, data=sess_data)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, EVENT_LIST)

    event = Event.objects.last()
    self.assertEqual(event.start_date, start_dt_obj)
    self.assertEqual(event.end_date, end_dt_obj)
        

  def test_create_event(self):
    url = reverse('create_event')
    
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, CREATE_EVENT)

    new_event_name = 'Test Event_Baru'
    start_dt_obj = datetime.datetime.strptime(self.start_date, self.strpformat).date()
    end_dt_obj = datetime.datetime.strptime(self.end_date, self.strpformat).date()
    
    sess_data = {
      'event_name': new_event_name,
      'start_date': self.start_date,
      'end_date': self.end_date,
      'action': 'add_roles'
    }

    data = {
      'num_fields':1,
      'role_field_0':'PO',
      'honor_field_0':10000,
      'pph_field_0': 10,
      'dropdown-select_0':'111'
    }

    response = self.client.post(url, data=sess_data)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'input_employee.html')
    
    session_data = self.client.session
    self.assertEqual(session_data['event_name'], new_event_name)
    self.assertEqual(session_data['start_date'], self.start_date)
    self.assertEqual(session_data['end_date'], self.end_date)
    
    response = self.client.post(reverse('input_employee_to_event'), data)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, EVENT_LIST)

    event = Event.objects.last()
    self.assertEqual(event.creator, self.account)
    self.assertEqual(event.event_name, new_event_name)
    self.assertEqual(Event.objects.count(), 1)
    self.assertEqual(event.start_date, start_dt_obj)
    self.assertEqual(event.end_date, end_dt_obj)
    
    event_employee1 = EventEmployee.objects.get(employee=self.pegawai1)
    self.assertEqual(event_employee1.role, 'PO')
    self.assertEqual(event_employee1.honor, 10000)
    self.assertEqual(event_employee1.pph, 10)


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
      start_date='2022-04-27',
      end_date='2022-05-28',
      expense=100000,
      sk_file=self.binary_data
    )
    self.assertIsInstance(event, Event)
    self.assertEqual(event.creator, self.account)
    self.assertEqual(event.event_name, self.event_name)
    self.assertLess(event.start_date, event.end_date)
    self.assertEqual(event.expense, 100000)
    self.assertEqual(event.sk_file, self.binary_data)
    
  def test_create_event_will_add_log(self):
    sess_data = {
      'event_name':self.event_name,
      'start_date':'2022-03-15',
      'end_date':'2022-06-12',
    }

    self.client.post(reverse('create_event'), data=sess_data)
    self.assertEqual(len(Log.objects.all()), 1)
    
    action = 'Create ' + self.event_name + ' event'
    self.assertTrue(Log.objects.filter(action=action).first())

  def test_create_event_employee(self):
    event = Event.objects.create(
      creator=self.account,
      event_name=self.event_name,
      start_date='2022-01-01',
      end_date='2022-02-02',
      expense=100000,
      sk_file=self.binary_data
    )

    event_employee = EventEmployee.objects.create(
      employee=self.pegawai,
      event=event
    )

    self.assertIsInstance(event_employee, EventEmployee)
    self.assertEqual(event_employee.employee, self.pegawai)
    self.assertEqual(event_employee.event, event)
  
class CreateUnauthorizedEventViewTestCase(TestCase):
  def test_unauthenticated_create(self):
    response = self.client.get(reverse('create_event'))
    self.assertEqual(response.status_code, 302)
  
  def test_unauthenticated_input(self):
    response = self.client.get(reverse('input_employee_to_event'))
    self.assertEqual(response.status_code, 302)


class ShowEventListViewTestCase(TestCase):
  def setUp(self):
    email = 'jona@gmail.com'

    self.event_name = 'Test Event Baru'
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

    self.event_name_1 = 'Event 1'
    self.event1 = Event.objects.create(
      creator=self.account,
      event_name=self.event_name_1,
      start_date='2022-04-23',
      end_date='2022-05-29',
      expense=10000,
      sk_file=self.binary_data
    )
    self.event2 = Event.objects.create(
      event_name='Event 2',
      start_date='2022-04-24',
      end_date='2022-05-30',
      expense=12000,
      sk_file=self.binary_data
    )
  
  def test_get_events(self):
    self.client.login(username='admin', password='admin123')
    response = self.client.get(reverse('get_events'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'event_list.html')
    self.assertContains(response, self.event_name_1)
    self.assertContains(response, 'Event 2')
    self.assertDictEqual(response.context['owner_data'], {self.event_name_1: True})

  def test_get_events_unauthenticated(self):
    response = self.client.get(reverse('get_events'))
    self.assertRedirects(response, '/login?next=/event/')

  def test_get_options_view(self):
    Pegawai.objects.create(
      email = 'johndoer1@gmail.com',
      employee_no = '190756565',
      employee_name = 'Test Pegawai 1',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335365',
      nomor_npwp = '247128654',
      alamat_npwp = 'Jl. Hj. Halimah Saerang I No. 1 RT. 004/02 Kukusan Beji Depok'
    )
    Pegawai.objects.create(
      email = 'johndoer2@gmail.com',
      employee_no = '190756566',
      employee_name = 'Test Pegawai 2',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335366',
      nomor_npwp = '247128652',
      alamat_npwp = 'Jl. Hj. Halimah Saerang I No. 2 RT. 004/02 Kukusan Beji Depok')
  
    Pegawai.objects.create(
      email = 'johndoer3@gmail.com',
      employee_no = '190756567',
      employee_name = 'Test Pegawai 3',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '247128659',
      alamat_npwp = 'Jl. Hj. Halimah Saerang I No. 3 RT. 004/02 Kukusan Beji Depok'
    )

    response = self.client.get(reverse('get_options'), data={'search': 'Test'})
    self.assertEqual(response.status_code, 200)
    self.assertJSONEqual(str(response.content, encoding='utf8'), [
      {'employee_no': '190756565', 'employee_name': 'Test Pegawai 1'},
      {'employee_no': '190756566', 'employee_name': 'Test Pegawai 2'},
      {'employee_no': '190756567', 'employee_name': 'Test Pegawai 3'},
    ])



class EventEmployeeModelTestCase(TestCase):
  @classmethod
  def setUpTestData(cls):
    email = 'jona@gmail.com'
    cls.binary_data = b'some binary data 1'
    cls.user = User.objects.create_user(
      username='admin', 
      password='admin123', 
      email='adminkocak@gmail.com'
    )

    cls.account = Account.objects.create(
      user = cls.user,
      username = 'jonikeren',
      email = email,
      role = 'User',
      is_first_login = True
    )

    cls.event = Event.objects.create(
      event_name='Test Event Baru',
      start_date='2023-01-01',
      end_date='2023-01-02',
    )

    cls.pegawai = Pegawai.objects.create(
      email = 'johndoer2@gmail.com',
      employee_no = '190756565',
      employee_name = 'Jonyy',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '247128658',
      alamat_npwp = 'Jl. Hj. Halimah Saerang I No. 1 RT. 004/02 Kukusan Beji Depok'
    )

    cls.event_employee = EventEmployee.objects.create(
      employee=cls.pegawai,
      event=cls.event,
      honor=1000,
      pph=10,
      role='Admin'
    )

  def test_employee_field(self):
      field = EventEmployee._meta.get_field('employee')
      self.assertEqual(field.related_model, Pegawai)

  def test_event_field(self):
    field = EventEmployee._meta.get_field('event')
    self.assertEqual(field.related_model, Event)

  def test_honor_field(self):
    field = EventEmployee._meta.get_field('honor')
    self.assertEqual(field.default, 0)
    self.assertEqual(field.validators[0].limit_value, 0)

  def test_pph_field(self):
    field = EventEmployee._meta.get_field('pph')
    self.assertEqual(field.default, 0)
    self.assertEqual(field.validators[0].limit_value, 0)

  def test_role_field(self):
    field = EventEmployee._meta.get_field('role')
    self.assertEqual(field.max_length, 100)
    self.assertEqual(field.null, True)

  def test_event_employee_creation(self):
    self.assertEqual(self.event_employee.employee, self.pegawai)
    self.assertEqual(self.event_employee.event, self.event)
    self.assertEqual(self.event_employee.honor, 1000)
    self.assertEqual(self.event_employee.pph, 10)
    self.assertEqual(self.event_employee.role, 'Admin')
  

class ValidationTests(TestCase):

  def test_validate_event_employee_fields(self):
    pph = 100000
    honor = 200000
    validate_event_employee_fields(pph, honor)
    
    pph = -100000
    honor = 200000
    with self.assertRaises(ValidationError):
      validate_event_employee_fields(pph, honor)
    
    pph = 100000
    honor = -200000
    with self.assertRaises(ValidationError):
      validate_event_employee_fields(pph, honor)


class InputEmployeeToEventTestCase(TestCase):
  def setUp(self):
    self.client = Client()
    self.start_date = '2023-03-22'
    self.end_date   = '2023-03-25'
    self.user = User.objects.create_user(
      username='admin5', 
      password='admin345', 
      email='adminkacok@gmail.com'
    )
    self.account = Account.objects.create(
      user = self.user,
      username = 'jonakeren',
      email = 'jokimak@gmail.com',
      role = 'User',
      is_first_login = True
    )
    self.sess_data = {
      'event_name': 'Event Paling Baru',
      'start_date': self.start_date,
      'end_date': self.end_date,
      'action': 'add_roles'
    }
    self.pegawai = Pegawai.objects.create(
      email = 'johndoer5@gmail.com',
      employee_no = '123',
      employee_name = 'Jonyz',
      employee_category = 'Staff',
      job_status = 'Administrasi',
      grade_level = '-',
      employment_status = 'Kontrak',
      nama_di_rekening = 'karyawankeren',
      nama_bank = 'Mandiri',
      nomor_rekening = '4971335367',
      nomor_npwp = '247128658',
      alamat_npwp = 'Jl. Hj. Halimah Saerang I No. 9 RT. 004/02 Kukusan Beji Depok'
    )
    self.event_data = {
        'num_fields': 1,
        'dropdown-select_0': '123',
        'role_field_0': 'Admin',
        'honor_field_0': '-100',
        'pph_field_0': '-200',
    }
    self.client.login(username='admin5', password='admin345')

  def test_input_employee_to_event_with_negative_honor_and_pph(self):
    self.client.post(reverse('create_event'), data=self.sess_data)
    response = self.client.post(reverse('input_employee_to_event'), data=self.event_data, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Event List')
    self.assertEqual(abs(int(self.event_data['honor_field_0'])), 100)
    self.assertEqual(abs(int(self.event_data['pph_field_0'])), 200)