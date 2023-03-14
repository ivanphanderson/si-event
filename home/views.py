from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import Account

@login_required(login_url='/login')
def home(request):
    navbar_admin = []
    acc = Account.objects.get(user=request.user)
    if acc.role == 'Admin':
        navbar_admin.append('Create Account')
    
    context = {'navbar_admin':navbar_admin}

    return render(request, 'home.html', context)