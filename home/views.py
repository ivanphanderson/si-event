from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import Account

@login_required(login_url='/login')
def home(request):
    acc = Account.objects.get(user=request.user)
    context = {
        'role': acc.role,
    }
    return render(request, 'home.html', context)

@login_required(login_url='/login')
def forbidden(request):
    acc = Account.objects.get(user=request.user)
    context = {
        'role': acc.role,
    }
    return render(request, 'forbidden.html', context)