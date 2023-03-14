from django.shortcuts import render
from log.models import Log
from datetime import date, datetime


def display_log(request):
    log_list = Log.objects.all().order_by('-date')
    context = {
        'data': log_list
    }
    return render(request, "log.html", context)

def add_log(user, action):
    current_date =  date.today().strftime("%b %d, %Y")
    current_time =  datetime.now().strftime("%H:%M:%S")
    log = Log(user=user, date=current_date, timestamp=current_time, action=action)
    log.save()
