from django.db.models import F
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Account
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

UNEXPECTED_HTML = 'unexpected.html'
AKUN_TIDAK_DITEMUKAN = 'Akun Tidak Ditemukan'

@require_GET
@login_required(login_url='/login')
def read_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        context = {}
        all_account = Account.objects.all().order_by(F('user__is_active').desc(), 'username')
        context['all_account'] = all_account
        return render(request, 'read_akun.html', context)
    else:
        return render(request, UNEXPECTED_HTML)

@require_GET
@login_required(login_url='/login')
def update_akun(request, id):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        if id.isdigit() and Account.objects.filter(id=id).first():
            account_update = Account.objects.filter(id=id).first()
            context = {}
            context['account'] = account_update
            return render(request, 'update_akun.html', context)
        else:
            return render(request, UNEXPECTED_HTML, {'message': AKUN_TIDAK_DITEMUKAN})
    else:
        return render(request, UNEXPECTED_HTML)
    
@require_POST
@login_required(login_url='/login')
def submit_update_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        id_akun = request.POST.get("id_akun")
        if id_akun.isdigit() and Account.objects.filter(id=id_akun).first():
            account_update = Account.objects.filter(id=id_akun).first()
            role_baru = request.POST.get("role")
            account_update.role = role_baru
            account_update.save()
            return redirect('account:read_akun')
        else:
            return render(request, UNEXPECTED_HTML, {'message': AKUN_TIDAK_DITEMUKAN})
    else:
        return render(request, UNEXPECTED_HTML)

@require_POST
@login_required(login_url='/login')
def ganti_status_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        id_akun = request.POST.get("id_akun")
        if id_akun.isdigit() and Account.objects.filter(id=id_akun).first():
            account_delete = Account.objects.filter(id=id_akun).first()
            user = account_delete.user
            user.is_active = not user.is_active
            user.save()
            return redirect('account:read_akun')
        else:
            return render(request, UNEXPECTED_HTML, {'message': AKUN_TIDAK_DITEMUKAN})
    else:
        return render(request, UNEXPECTED_HTML)
    