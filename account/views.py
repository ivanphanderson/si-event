from .models import Account, User, NonSSOAccount
from .forms import AccountForm, UbahPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from auth_sso.models import SSOUIAccount

AKUN_TIDAK_DITEMUKAN = "Account not found"
HALAMAN_UBAH_PASSWORD_LOGGED_IN_HTML = "halaman_ubah_password_logged_in.html"
HOME_URL = "home:home"
FORBIDDEN_URL = "home:forbidden"
ACCOUNT_CREATION_FAILED = (
    "Account creation failed, make sure all field is filled correctly."
)
NO_ACCESS_TO_READ_ACCOUNT = "You don't have access to read account!"
NO_ACCESS_TO_UPDATE_ACCOUNT = "You don't have access to update account!"
LOGIN_URL = "authentication:login"


@login_required(login_url=LOGIN_URL)
@require_http_methods(["GET", "POST"])
def register_account(request):
    user = request.user
    account = Account.objects.get(user=user)

    if account.role != "Admin":
        return redirect("/home/forbidden")

    form = UserCreationForm(request.POST)
    form2 = AccountForm(request.POST)
    msg = []
    error_lst = []
    roles = ["Admin", "User", "Staff Keuangan"]

    if request.method == "POST":
        if form.is_valid() and form2.is_valid():
            username = form2.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form2.cleaned_data["email"]
            role = form2.cleaned_data["role"]

            if Account.objects.filter(email=email).exists():
                msg.append("A user with that email already exists.")
                msg.append(ACCOUNT_CREATION_FAILED)

            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email
                )
                account_non_sso = NonSSOAccount(
                    user=user, username=username, email=email, role=role
                )
                acc = Account(
                    user=user,
                    accNonSSO=account_non_sso,
                    username=username,
                    email=email,
                    role=role,
                    accountType="Non SSO",
                )
                if role == "Admin":
                    user.is_staff = True
                user.save()
                account_non_sso.save()
                acc.save()
                messages.success(request, "Account is created successfully.")
                return redirect("/account")
        else:
            msg.append(ACCOUNT_CREATION_FAILED)
            error_lst = list(form.errors.values())
    context = {
        "form2": form2,
        "msg": msg,
        "errors": error_lst,
        "roles": roles,
        "role": account.role,
    }
    return render(request, "register_account.html", context)


@require_GET
@login_required(login_url=LOGIN_URL)
def ubah_password(request):
    context = {"is_ubah_password": True}
    return render(request, HALAMAN_UBAH_PASSWORD_LOGGED_IN_HTML, context)


@require_POST
@login_required(login_url=LOGIN_URL)
def submit_ubah_password(request):
    form = UbahPasswordForm(request.POST)
    if form.is_valid():
        current_password = form.cleaned_data["current_password"]
        if check_password(current_password, request.user.password):
            password = form.cleaned_data["new_password"]
            user = request.user
            try:
                validate_password(password)
            except ValidationError as e:
                context = {}
                context["messages"] = e
                return render(request, HALAMAN_UBAH_PASSWORD_LOGGED_IN_HTML, context)

            user.set_password(form.cleaned_data["new_password"])
            user.save()
            account = NonSSOAccount.objects.get(user=user)
            account.is_first_login = False
            account.save()
            messages.info(request, "Password has been changed, please login again.")
            return redirect("/login")
        return render(
            request,
            HALAMAN_UBAH_PASSWORD_LOGGED_IN_HTML,
            {"messages": ["Current password is incorrect!"]},
        )
    return render(
        request,
        HALAMAN_UBAH_PASSWORD_LOGGED_IN_HTML,
        {"messages": ["Make sure new password and its confirmation is the same!"]},
    )


@require_GET
@login_required(login_url=LOGIN_URL)
def read_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        context = {}
        all_account = Account.objects.all().order_by(
            F("user__is_active").desc(), "username"
        )
        context["all_account"] = all_account
        context["role"] = account.role
        return render(request, "read_akun.html", context)
    else:
        return redirect(FORBIDDEN_URL)


@require_GET
@login_required(login_url=LOGIN_URL)
def update_akun(request, id):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        if id.isdigit() and Account.objects.filter(id=id).first():
            account_update = Account.objects.filter(id=id).first()
            if account_update.user.is_superuser or account_update.user == user:
                return redirect(FORBIDDEN_URL)
            context = {}
            context["account"] = account_update
            context["role"] = account.role
            return render(request, "update_akun.html", context)
        else:
            return redirect(FORBIDDEN_URL)
    else:
        return redirect(FORBIDDEN_URL)


@require_POST
@login_required(login_url=LOGIN_URL)
def submit_update_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        id_akun = request.POST.get("id_akun")
        if id_akun.isdigit() and Account.objects.filter(id=id_akun).first():
            account_update = Account.objects.filter(id=id_akun).first()
            if account_update.user.is_superuser or account_update.user == user:
                return redirect(FORBIDDEN_URL)
            role_baru = request.POST.get("role")
            account_update.role = role_baru
            account_update.save()
            if account_update.accNonSSO != None:
                acc_non_sso = NonSSOAccount.objects.filter(
                    username=account_update.username
                ).first()
                acc_non_sso.role = role_baru
                acc_non_sso.save()
            else:
                acc_sso = SSOUIAccount.objects.filter(
                    username=account_update.username
                ).first()
                acc_sso.role = role_baru
                acc_sso.save()
            messages.success(
                request,
                f"Role of {account_update.username}'s account has been changed successfully.",
            )
            return redirect("account:read_akun")
        else:
            return redirect(FORBIDDEN_URL)
    else:
        return redirect(FORBIDDEN_URL)


@require_POST
@login_required(login_url=LOGIN_URL)
def ganti_status_akun(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    if account.role == "Admin":
        id_akun = request.POST.get("id_akun")
        if id_akun.isdigit() and Account.objects.filter(id=id_akun).first():
            account_delete = Account.objects.filter(id=id_akun).first()
            if account_delete.user.is_superuser or account_delete.user == user:
                return redirect(FORBIDDEN_URL)
            user = account_delete.user
            user.is_active = not user.is_active
            user.save()
            msg1 = "activated"
            if not user.is_active:
                msg1 = "deactivated"
            messages.info(
                request,
                f"{account_delete.username}'s account has been {msg1} successfully.",
            )
            return redirect("account:read_akun")
        else:
            return redirect(FORBIDDEN_URL)
    else:
        return redirect(FORBIDDEN_URL)
