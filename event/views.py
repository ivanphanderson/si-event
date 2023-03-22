from django.shortcuts import render, redirect

from .models import Event, EventEmployee

from pegawai.models import Pegawai
from pegawai.handler import DataCleaner

from account.models import Account
from authentication.views import login_user

from utils.converter import convert_to_data


def create_event(request):
  if (not request.user.is_authenticated):
    return redirect('authentication:login')
  
  user_id = request.user.id
  account = Account.objects.get(id=user_id)

  if (request.method == 'POST'):
    body = request.POST

    event_name   = body.get('event_name')
    start_date   = body.get('start_date')
    end_date     = body.get('end_date')
    expense      = body.get('expense')
    tax          = body.get('tax')
    raw_list_emp = str(body.get('list_employee_no')).strip()

    list_emp_no = raw_list_emp.split() if raw_list_emp else []

    new_event  = Event.objects.create(
      creator=account,
      event_name=event_name,
      start_date=start_date,
      end_date=end_date,
      expense=expense,
      tax=tax
    )

    _input_pegawai_to_event(request, list_emp_no, new_event)

    return render(request, 'done.html')
  return render(request, 'create_event.html')


def _input_pegawai_to_event(request, list_emp_no, new_event):
  if 'pegawai_file' in request.FILES:
    pegawai_file = request.FILES['pegawai_file'].read()
    data_pegawai = convert_to_data(pegawai_file)
    data_cleaner = DataCleaner(None)
    cleaned_data = data_cleaner.functionality(data_pegawai, dict())[0]

    non_blank_idx = next((i for i, row in enumerate(cleaned_data) if row[0] != ''), -1)
    if non_blank_idx != -1:
      for row in cleaned_data[non_blank_idx+1:]:
        target_pegawai = Pegawai.objects.get(employee_no=row[2])
        EventEmployee.objects.create(employee=target_pegawai, event=new_event)
    
  for emp_no in list_emp_no:
    if emp_no and emp_no != 'None':
      target_pegawai = Pegawai.objects.get(employee_no=emp_no)
      EventEmployee.objects.create(employee=target_pegawai, event=new_event)