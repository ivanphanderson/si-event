from django.shortcuts import render
from .models import PasswordOTP
from account.models import Account, User
from .forms import ForgetPasswordForm, NewPasswordForm
from .utils import send_forget_password_email, is_valid_referer_ubah_password_get, is_valid_referer_ubah_password_post
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

AKSES_ILEGAL = 'Akses Ilegal'
FORGET_PASSWORD_HTML = 'forget_password.html'
UNEXPECTED_HTML = 'unexpected.html'
HALAMAN_UBAH_PASSWORD_HTML = 'halaman_ubah_password.html'

def auto_redirect(request):
    user = request.user
    if user.is_authenticated:
        return redirect('/home')
    else:
        return redirect('/login')

def login_user(request):
    navbar_admin = []
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            acc = Account.objects.get(user=user)
            if acc.role == 'Admin':
                navbar_admin.append('Create Account')
            if acc.is_first_login == True:
                return redirect('/account/ubah-password')
            else:
                return redirect('/home')
        else:
            messages.info(request, 'Username atau Password salah!')

    context = {'form':'form', 'navbar_admin':navbar_admin}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('/login')

@require_GET
def forget_password(request):
    return render(request, FORGET_PASSWORD_HTML)

@require_POST
def submit_forget_password(request):
    forget_password_form = ForgetPasswordForm(request.POST)
    if forget_password_form.is_valid():
        username = forget_password_form.cleaned_data['username']
        email = forget_password_form.cleaned_data['email']
        if Account.objects.filter(username=username, email=email):
            send_forget_password_email(username, email)
            return redirect('authentication:handle_otp', username=username)
        else:
            context = {'messages': ['Username dan email tidak sesuai']}
            return render(request, FORGET_PASSWORD_HTML, context)
    return render(request, FORGET_PASSWORD_HTML)

@require_GET
def handle_otp(request, username):
    return render(request, 'halaman_otp.html', {'username': username})

@require_POST
def submit_otp(request):
    username = request.POST.get("username")
    OTP = request.POST.get("OTP")
    otp_obj = PasswordOTP.objects.filter(username=username, OTP=OTP, is_redeem=False)
    if otp_obj.first():
        otp_obj = otp_obj.first()
        if otp_obj.valid_until > timezone.now():
            otp_obj.is_redeem = True
            otp_obj.save()
            return redirect('authentication:ubah_password', username=username)
    else:
        context = {'messages': ['Kode OTP salah/invalid'], 'username': username}
        return render(request, 'halaman_otp.html', context)
        

@require_GET
def ubah_password(request, username):
    http_referer = request.META.get('HTTP_REFERER', '')

    if not is_valid_referer_ubah_password_get(http_referer):
        return render(request, UNEXPECTED_HTML, {'message': AKSES_ILEGAL})

    otp = PasswordOTP.objects.filter(username=username, valid_until__gte=timezone.now(), is_redeem=True, is_changed=False).first()
    if not otp:
        return render(request, UNEXPECTED_HTML, {'message': AKSES_ILEGAL})
    
    return render(request, HALAMAN_UBAH_PASSWORD_HTML, {'username': username})

@require_POST
def submit_ubah_password(request):
    context = {}
    http_referer = request.META.get('HTTP_REFERER', '')
    if is_valid_referer_ubah_password_post(http_referer):
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            try:
                validate_password(password)
            except ValidationError as e:
                context['messages'] = e
                context['username'] = form.cleaned_data['username']
                return render(request, HALAMAN_UBAH_PASSWORD_HTML, context)
            username = form.cleaned_data['username']
            otp = PasswordOTP.objects.filter(username=username, is_redeem=True, is_changed=False).first()
            if not otp:
                return render(request, UNEXPECTED_HTML, {'message': AKSES_ILEGAL})
            
            otp.is_changed = True
            otp.save()
            
            user = User.objects.filter(username=username).first()
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            return render(request, "berhasil_ubah_password.html")

        
        context['messages'] = ['Password tidak sama']
        context['username'] = form.cleaned_data['username']
        return render(request, HALAMAN_UBAH_PASSWORD_HTML, context)
    return render(request, UNEXPECTED_HTML, {'message': AKSES_ILEGAL})
