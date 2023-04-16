from io import BytesIO
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.db.models import Sum
from event.models import Event, EventEmployee
from pegawai.models import Pegawai
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
import json
from .excel_downloader import excel_factory


def is_valid_queryparam(param):
    return param != '' and param is not None

def filter(request):
    qs = EventEmployee.objects.all()

    pegawai = request.GET.get('pegawai')
    date_min = request.GET.get('publishDateMin')
    date_max = request.GET.get('publishDateMax')
    event = request.GET.get('event')

    if is_valid_queryparam(date_min):
        e = Event.objects.filter(end_date__gte=date_min)
        qs = qs.filter(event__in=e)

    if is_valid_queryparam(date_max):
        ev = Event.objects.filter(end_date__lte=date_max)
        qs = qs.filter(event__in=ev)

    if is_valid_queryparam(pegawai) and pegawai != 'None':
        employee = Pegawai.objects.get(employee_name=pegawai)
        qs = qs.filter(employee=employee)

    if is_valid_queryparam(event) and event != 'None':
        ev = Event.objects.get(event_name=event)
        qs = qs.filter(event=ev.id)

    return qs, date_min, date_max, pegawai, event

@require_GET
@login_required(login_url='/login')
def filter_honor_view(request):
    user = request.user
    account = Account.objects.get(user=user)

    if account.role == 'Staff Keuangan':
        qs, date_min, date_max, pegawai, event = filter(request)

        context = {
            'queryset': qs,
            'date_min': date_min,
            'date_max': date_max,
            'pegawai': pegawai,
            'event': event,
            'categories': Event.objects.all(),
            'employees': Pegawai.objects.all(),
            'total_bruto': qs.aggregate(Sum('honor'))['honor__sum'],
            'total_pph': qs.aggregate(Sum('pph'))['pph__sum'],
            'total_netto': qs.aggregate(Sum('netto'))['netto__sum'],
            'role': account.role,
        }
        return render(request, "filter_form.html", context) 
    else:
        context = {
            'role': account.role,
        }
        return render(request, "forbidden.html", context)

@require_POST
def download_excel_from_data(request: HttpRequest, type: str):
    table_data: dict[str, dict[str, str]] = json.loads(request.body)
    content_dispotition  = 'attachment; filename=data pembayaran panitia event.xlsx' if type == 'standard' else 'attachment; filename=BTR dan memo.xlsx'
    excel_file = excel_factory(type).get_excel(table_data)

    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Dispotition'] = content_dispotition

    return response
