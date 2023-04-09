from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import Account
from django.views.decorators.http import require_GET

@require_GET
@login_required(login_url='/login')
def home(request):
    acc = Account.objects.get(user=request.user)
    context = {
        'role': acc.role,
    }
    return render(request, 'index.html', context)

@require_GET
@login_required(login_url='/login')
def forbidden(request):
    acc = Account.objects.get(user=request.user)
    context = {
        'role': acc.role,
    }
    return render(request, 'forbidden.html', context)
