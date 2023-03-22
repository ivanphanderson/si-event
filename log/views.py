from django.shortcuts import render
from log.models import Log
from datetime import date, datetime
from account.models import Account
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login')
def display_log(request):
    user = request.user
    account = Account.objects.get(user=user)

    if account.role == 'Admin':
        log_list = Log.objects.all().order_by('-date')
        context = {
            'data': log_list,
            'role': account.role,
            }
        return render(request, "log.html", context)
    else:
        context = {
            'role': account.role,
            }
        return render(request, "forbidden.html", context)

def add_log(user, action):
    current_date =  date.today().strftime("%b %d, %Y")
    current_time =  datetime.now().strftime("%H:%M:%S")
    log = Log(user=user, date=current_date, timestamp=current_time, action=action)
    log.save()
