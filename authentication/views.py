from django.shortcuts import render
from .models import PasswordOTP
from account.models import Account, User, NonSSOAccount
from .forms import ForgetPasswordForm, NewPasswordForm
from .utils import (
    send_forget_password_email,
    is_valid_referer_ubah_password_get,
    is_valid_referer_ubah_password_post,
)
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


AKSES_ILEGAL = "Illegal Access"
LOGIN_URL = "authentication:login"
FORGET_PASSWORD_HTML = "forget_password.html"
FORBIDDEN_HTML = "forbidden.html"
HALAMAN_UBAH_PASSWORD_HTML = "halaman_ubah_password.html"


@require_GET
def auto_redirect(request):
    user = request.user
    if user.is_authenticated:
        return redirect("home:home")
    else:
        return redirect(LOGIN_URL)


@require_http_methods(["GET", "POST"])
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                acc = NonSSOAccount.objects.get(user=user)
                login(request, user)
                if acc.is_first_login == True:
                    return redirect("account:ubah_password")
                else:
                    return redirect("home:home")
            except Exception:
                messages.info(request, "Account has not registered yet.")

        else:
            messages.info(request, "Wrong Username or Password!")

    context = {"form": "form"}
    return render(request, "login.html", context)


@require_GET
def logout_user(request):
    logout(request)
    return redirect(LOGIN_URL)


@require_GET
def forget_password(request):
    return render(request, FORGET_PASSWORD_HTML)


@require_POST
def submit_forget_password(request):
    forget_password_form = ForgetPasswordForm(request.POST)
    if forget_password_form.is_valid():
        username = forget_password_form.cleaned_data["username"]
        email = forget_password_form.cleaned_data["email"]
        if NonSSOAccount.objects.filter(username=username, email=email):
            send_forget_password_email(username, email)
            return redirect("authentication:handle_otp", username=username)
        else:
            context = {"messages": ["Username or Email is Wrong!"]}
            return render(request, FORGET_PASSWORD_HTML, context)
    return render(request, FORGET_PASSWORD_HTML)


@require_GET
def handle_otp(request, username):
    return render(request, "halaman_otp.html", {"username": username})


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
            return redirect("authentication:ubah_password", username=username)
    else:
        context = {"messages": ["Invalid/Wrong OTP Code"], "username": username}
        return render(request, "halaman_otp.html", context)


@require_GET
def ubah_password(request, username):
    http_referer = request.META.get("HTTP_REFERER", "")

    if not is_valid_referer_ubah_password_get(http_referer):
        return render(request, FORBIDDEN_HTML)

    otp = PasswordOTP.objects.filter(
        username=username,
        valid_until__gte=timezone.now(),
        is_redeem=True,
        is_changed=False,
    ).first()
    if not otp:
        return render(request, FORBIDDEN_HTML)

    return render(request, HALAMAN_UBAH_PASSWORD_HTML, {"username": username})


@require_POST
def submit_ubah_password(request):
    context = {}
    http_referer = request.META.get("HTTP_REFERER", "")
    if is_valid_referer_ubah_password_post(http_referer):
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            try:
                validate_password(password)
            except ValidationError as e:
                context["messages"] = e
                context["username"] = form.cleaned_data["username"]
                return render(request, HALAMAN_UBAH_PASSWORD_HTML, context)
            username = form.cleaned_data["username"]
            otp = PasswordOTP.objects.filter(
                username=username, is_redeem=True, is_changed=False
            ).first()
            if not otp:
                return render(request, FORBIDDEN_HTML)

            otp.is_changed = True
            otp.save()

            user = User.objects.filter(username=username).first()
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.info(
                request,
                "Password has been saved. Please login using your new password.",
            )
            return redirect(LOGIN_URL)

        context["messages"] = ["Password is not the same!"]
        context["username"] = form.cleaned_data["username"]
        return render(request, HALAMAN_UBAH_PASSWORD_HTML, context)
    return render(request, FORBIDDEN_HTML)
