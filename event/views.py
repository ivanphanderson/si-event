from django.shortcuts import render, redirect
from .models import Event, EventEmployee
from pegawai.models import Pegawai
from pegawai.views import add_log
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .validators import validate_event_employee_fields
from django.views.decorators.http import require_http_methods
from django.db.models import Sum


CREATE_EVENT = "create_event.html"
EVENT_LIST = "event_list.html"
FORBIDDEN_URL = "home:forbidden"
LOGIN_URL = "authentication:login"


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET", "POST"])
def create_event(request):
    if request.method == "POST":
        body = request.POST

        event_name = body.get("event_name")
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        action = body.get("action")

        if action == "add_roles":
            request.session["event_name"] = event_name
            request.session["start_date"] = start_date
            request.session["end_date"] = end_date
            return render(request, "input_employee.html")
        else:
            account = Account.objects.get(user=request.user)
            Event.objects.create(
                creator=account,
                event_name=event_name,
                start_date=start_date,
                end_date=end_date,
            )
            action = "Create " + event_name + " event"
            add_log(account, action)

            request.session.pop("event_name", None)
            request.session.pop("start_date", None)
            request.session.pop("end_date", None)
            return get_events(request, action)
    account = Account.objects.get(user=request.user)
    if account.role == "User":
        return render(request, CREATE_EVENT)
    else:
        return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def input_employee_to_event(request):
    account = Account.objects.get(user=request.user)
    form_data = request.POST

    if form_data["num_fields"] != "":
        num_fields = int(form_data["num_fields"])
    else:
        num_fields = 0

    total_honor = 0
    for idx in range(num_fields):
        if form_data[f"honor_field_{idx}"] != "":
            total_honor += abs(int(form_data[f"honor_field_{idx}"]))

    new_event = Event.objects.create(
        creator=account,
        event_name=request.session["event_name"],
        start_date=request.session["start_date"],
        end_date=request.session["end_date"],
        expense=total_honor,
    )

    action = "Create " + request.session["event_name"] + " event"
    add_log(Account.objects.get(user=request.user), action)

    for idx in range(num_fields):
        if f"dropdown-select_{idx}" in form_data:
            employee_no = form_data[f"dropdown-select_{idx}"]
            role = form_data[f"role_field_{idx}"]
            honor = form_data[f"honor_field_{idx}"]
            pph = form_data[f"pph_field_{idx}"]

            role, pph, honor = validate_event_employee_fields(role, pph, honor, idx)
            if str(employee_no).isnumeric():
                pegawai = Pegawai.objects.get(employee_no=employee_no)
                EventEmployee.objects.create(
                    employee=pegawai, event=new_event, honor=honor, pph=pph, role=role
                )

    return get_events(request, action)


@require_http_methods(["GET"])
def get_options(request):
    search_term = request.GET.get("search", "")
    employees = Pegawai.objects.filter(
        Q(employee_no__icontains=search_term) | Q(employee_name__icontains=search_term)
    )
    employees = [
        {"employee_no": e.employee_no, "employee_name": e.employee_name}
        for e in employees
    ]
    return JsonResponse(employees, safe=False)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET", "POST"])
def get_events(request, success_message=None):
    account = Account.objects.get(user=request.user)
    event_data = Event.objects.all().order_by("event_name")
    owner_data = dict()

    for event in event_data:
        if event.creator == account or account.role == "Staff Keuangan":
            owner_data[f"{event.event_name}"] = True

    if success_message is not None:
        return render(
            request,
            EVENT_LIST,
            {
                "event_data": event_data,
                "owner_data": owner_data,
                "success_message": success_message,
                "role": account.role,
            },
        )

    return render(
        request,
        EVENT_LIST,
        {"event_data": event_data, "owner_data": owner_data, "role": account.role},
    )


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET"])
def riwayat_events(request):
    account = Account.objects.get(user=request.user)
    if account.role == "User":
        event_data = Event.objects.filter(creator=account).order_by("event_name")
        return render(
            request,
            "riwayat_event.html",
            {"event_data": event_data, "role": account.role},
        )
    else:
        return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET"])
def detail_event(request, id):
    context = {}
    account = Account.objects.get(user=request.user)
    context["account"] = account
    context["role"] = account.role

    if id.isdigit() and Event.objects.filter(id=id).first():
        event = Event.objects.get(id=id)
        if event.creator != account and account.role == "User":
            return redirect(FORBIDDEN_URL)

        event_employees = EventEmployee.objects.filter(event=event)
        context["event"] = event
        context["event_employees"] = event_employees

        event_emps = EventEmployee.objects.all().filter(event=event.id)
        pph_in_rp = 0
        for emp in event_emps:
            pph_in_rp += emp.pph/100.0 * emp.honor
        context["total_bruto"] = event_emps.aggregate(Sum("honor"))["honor__sum"]
        context["total_pph"] = int(pph_in_rp)
        context["total_netto"] = event_emps.aggregate(Sum("netto"))["netto__sum"]

        return render(request, "detail_event.html", context)
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET"])
def update_event(request, id):
    context = {}
    account = Account.objects.get(user=request.user)
    context["role"] = account.role
    if id.isdigit() and Event.objects.filter(id=id).first():
        event = Event.objects.get(id=id)
        if event.creator != account:
            return redirect(FORBIDDEN_URL)
        context["event"] = event
        return render(request, "update_event.html", context)
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def submit_update_event(request, id):
    context = {}
    account = Account.objects.get(user=request.user)
    context["role"] = account.role
    if id.isdigit() and Event.objects.filter(id=id).first():
        event = Event.objects.get(id=id)
        if event.creator != account:
            return redirect(FORBIDDEN_URL)
        body = request.POST
        event.event_name = body.get("event_name")
        event.start_date = body.get("start_date")
        event.end_date = body.get("end_date")
        event.save()

        action = f"Updated {event.event_name} event"
        add_log(Account.objects.get(user=request.user), action)
        return redirect(f"/event/detail/{id}")
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET"])
def input_employee_to_existing_event(request, id):
    context = {}
    account = Account.objects.get(user=request.user)
    context["role"] = account.role
    if id.isdigit() and Event.objects.filter(id=id).first():
        event = Event.objects.get(id=id)
        if event.creator != account:
            return redirect(FORBIDDEN_URL)
        context["event"] = event
        return render(request, "input_employee_to_existing_event.html", context)
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def submit_input_employee_to_existing_event(request, id):
    account = Account.objects.get(user=request.user)
    if id.isdigit() and Event.objects.filter(id=id).first():
        event = Event.objects.get(id=id)
        if event.creator != account:
            return redirect(FORBIDDEN_URL)
        form_data = request.POST

        if form_data["num_fields"] != "":
            num_fields = int(form_data["num_fields"])
        else:
            num_fields = 0

        total_honor = calculate_total_honor(form_data, num_fields)

        event.expense += total_honor
        event.save()

        action = f"Added Employee to {event.event_name} event"
        add_log(Account.objects.get(user=request.user), action)

        for idx in range(num_fields):
            if f"dropdown-select_{idx}" in form_data:
                process_employee_data(event, form_data, idx)

        messages.success(request, "Employees is added successfully.")
        return redirect(f"/event/detail/{id}")
    return redirect(FORBIDDEN_URL)


def calculate_total_honor(form_data, num_fields):
    total_honor = 0
    for idx in range(num_fields):
        honor_field = form_data.get(f"honor_field_{idx}")
        if honor_field:
            total_honor += abs(int(honor_field))
    return total_honor


def process_employee_data(event, form_data, idx):
    employee_no = form_data[f"dropdown-select_{idx}"]
    role = form_data[f"role_field_{idx}"]
    honor = form_data[f"honor_field_{idx}"]
    pph = form_data[f"pph_field_{idx}"]
    role, pph, honor = validate_event_employee_fields(role, pph, honor, idx)
    if str(employee_no).isnumeric():
        pegawai = Pegawai.objects.get(employee_no=employee_no)
        EventEmployee.objects.create(
            employee=pegawai, event=event, honor=honor, pph=pph, role=role
        )


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET"])
def update_event_employee_by_id(request, id):
    context = {}
    account = Account.objects.get(user=request.user)
    context["role"] = account.role
    if id.isdigit() and EventEmployee.objects.filter(id=id).first():
        event_employee = EventEmployee.objects.get(id=id)
        context["event_employee"] = event_employee
        if event_employee.event.creator != account:
            return redirect(FORBIDDEN_URL)
        return render(request, "update_event_employee.html", context)
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def update_employee_to_event_by_id(request, id):
    account = Account.objects.get(user=request.user)
    form_data = request.POST
    if id.isdigit() and EventEmployee.objects.filter(id=id).first():
        event_employee = EventEmployee.objects.get(id=id)
        event = event_employee.event

        if event.creator != account:
            return redirect(FORBIDDEN_URL)

        employee_no = form_data["dropdown-select_0"]
        role = form_data["role_field_0"]
        honor = form_data["honor_field_0"]
        pph = form_data["pph_field_0"]

        role, pph, honor = validate_event_employee_fields(role, pph, honor, 0)
        if str(employee_no).isdigit():
            pegawai = Pegawai.objects.get(employee_no=employee_no)

            event.expense = event.expense - event_employee.honor + honor
            event.save()

            event_employee.employee = pegawai
            event_employee.role = role
            event_employee.honor = honor
            event_employee.pph = pph
            event_employee.save()

        action = f"Updated {event_employee.employee.employee_name} in {event.event_name} event"
        add_log(Account.objects.get(user=request.user), action)

        messages.success(
            request, f"{event_employee.employee.employee_name} is updated successfully."
        )
        return redirect(f"/event/detail/{event.id}")
    return redirect(FORBIDDEN_URL)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def delete_event_employee_by_id(request, id):
    account = Account.objects.get(user=request.user)
    if id.isdigit() and EventEmployee.objects.filter(id=id).first():
        event_employee = EventEmployee.objects.get(id=id)
        event = event_employee.event
        if event.creator != account:
            return redirect(FORBIDDEN_URL)
        event_employee.delete()

        action = f"Deleted {event_employee.employee.employee_name} from {event.event_name} event"
        add_log(Account.objects.get(user=request.user), action)

        messages.success(
            request, f"{event_employee.employee.employee_name} is deleted successfully."
        )
        return redirect(f"/event/detail/{event.id}")
    return redirect(FORBIDDEN_URL)
