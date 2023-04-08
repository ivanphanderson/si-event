from django.shortcuts import render, redirect
from .models import Event, EventEmployee
from pegawai.models import Pegawai
from pegawai.handler import DataCleaner
from pegawai.views import add_log
from account.models import Account
from utils.converter import convert_to_data
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse
from .validators import validate_event_employee_fields
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

CREATE_EVENT = 'create_event.html'
EVENT_LIST = 'event_list.html'

@login_required(login_url='/login')
@require_http_methods(['GET', 'POST'])
def create_event(request):
  if (request.method == 'POST'):
    body = request.POST

    event_name = body.get('event_name')
    start_date = body.get('start_date')
    end_date   = body.get('end_date')
    action     = body.get('action')

    if action == 'add_roles':
      request.session['event_name'] = event_name
      request.session['start_date'] = start_date
      request.session['end_date']   = end_date
      return render(request, 'input_employee.html')
    else:
      account = Account.objects.get(user=request.user)
      Event.objects.create(
        creator=account,
        event_name=event_name,
        start_date=start_date,
        end_date=end_date,
      )
      action = 'Create ' + event_name + ' event'
      add_log(account, action)

      request.session.pop('event_name', None)
      request.session.pop('start_date', None)
      request.session.pop('end_date', None)
      return get_events(request, action)
  return render(request, CREATE_EVENT)


@login_required(login_url='/login')
@require_http_methods(['POST'])
def input_employee_to_event(request):
  account    = Account.objects.get(user=request.user)
  form_data  = request.POST

  if form_data['num_fields'] != '':
    num_fields = int(form_data['num_fields'])
  else:
    num_fields = 0

  total_honor = 0
  for idx in range(num_fields):
    if form_data[f'honor_field_{idx}'] != '':
      total_honor += abs(int(form_data[f'honor_field_{idx}']))
  
  new_event = Event.objects.create(
    creator=account,
    event_name=request.session['event_name'],
    start_date=request.session['start_date'],
    end_date=request.session['end_date'],
    expense=total_honor,
  )

  action = 'Create ' + request.session['event_name'] + ' event'
  add_log(Account.objects.get(user=request.user), action)

  for idx in range(num_fields):
    if f'dropdown-select_{idx}' in form_data:
      employee_no = form_data[f'dropdown-select_{idx}']
      role        = form_data[f'role_field_{idx}']
      honor       = form_data[f'honor_field_{idx}']
      pph         = form_data[f'pph_field_{idx}']

      role, pph, honor  = validate_event_employee_fields(role, pph, honor, idx)
      if str(employee_no).isnumeric():
        pegawai = Pegawai.objects.get(employee_no=employee_no)
        EventEmployee.objects.create(employee=pegawai, event=new_event, honor=honor, pph=pph, role=role)
  
  return get_events(request, action)


@require_http_methods(['GET'])
def get_options(request):
  search_term = request.GET.get('search', '')
  employees = Pegawai.objects.filter(Q(employee_no__icontains=search_term) | Q(employee_name__icontains=search_term))
  employees = [{'employee_no': e.employee_no, 'employee_name': e.employee_name} for e in employees]
  return JsonResponse(employees, safe=False)


@login_required(login_url='/login')
@require_http_methods(['GET', 'POST'])
def get_events(request, success_message=None):
  account = Account.objects.get(user=request.user)
  event_data = Event.objects.all().order_by('event_name')
  owner_data = dict()
    
  for event in event_data:
    if event.creator == account:
      owner_data[f'{event.event_name}'] = True

  if success_message is not None:
    return render(request, EVENT_LIST, {'event_data':event_data, 'owner_data':owner_data, 'success_message':success_message})
  
  return render(request, EVENT_LIST, {'event_data':event_data, 'owner_data':owner_data})