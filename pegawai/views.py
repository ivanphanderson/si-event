from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from utils.converter import convert_to_data
from .models import Pegawai
from django.template.response import TemplateResponse
from typing import List
from .handler import DataCleaner, ValidColumnNameChecker, UniqueEmailInFileChecker
from django.contrib.auth.mixins import LoginRequiredMixin
from log.views import add_log
from account.models import Account
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from pembayaran.excel_downloader import excel_factory


URL_AUTH = "authentication:login"
FORBIDDEN_PAGE = "forbidden.html"

data_pegawai_cols = [
    "No",
    "Employee No.",
    "Employee Name",
    "Employee Category",
    "Job Status",
    "Grade Level",
    "Employment Status",
    "Email",
    "NAMA DI REKENING",
    "NAMA BANK",
    "NO REKENING",
    "Nomor NPWP",
    "Alamat NPWP",
]


class AddPegawaiView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy(URL_AUTH)

    def get(self, request, *args, **kwargs):
        if len(Pegawai.objects.all()) > 0:
            return HttpResponseRedirect(reverse("pegawai:update_pegawai"))
        return super(AddPegawaiView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        user = self.request.user
        account = Account.objects.get(user=user)

        if account.role == "Admin":
            template_name = "add_pegawai.html"
        else:
            template_name = FORBIDDEN_PAGE
        return [template_name]

    def get_context_data(self, **kwargs):
        user = self.request.user
        account = Account.objects.get(user=user)

        context = super().get_context_data(**kwargs)
        context["role"] = account.role
        context["title"] = "Add Employee Data"

        return context


class SavePegawaiToDatabase(CreateView):
    def check_data(self, data: List[List[str]]) -> List:
        unique_email_checker = UniqueEmailInFileChecker(None)
        valid_column_name_checker = ValidColumnNameChecker(unique_email_checker)
        data_cleaner = DataCleaner(valid_column_name_checker)
        return data_cleaner.functionality(data, dict())

    def post(self, request, *args, **kwargs):
        try:
            bytes_file = request.FILES["file"].read()
            data: List[List[str]] = convert_to_data(bytes_file)

            check_data_result = self.check_data(data)
            data = check_data_result[0]
            index_start_data = check_data_result[1]["records_index"]

            for index in range(index_start_data, len(data)):
                new_pegawai = Pegawai(
                    email=data[index][7].strip(),
                    employee_no=str(int(data[index][1].strip())),
                    employee_name=data[index][2].strip(),
                    employee_category=data[index][3].strip(),
                    job_status=data[index][4].strip(),
                    grade_level=data[index][5].strip(),
                    employment_status=data[index][6].strip(),
                    nama_di_rekening=data[index][8].strip(),
                    nama_bank=data[index][9].strip(),
                    nomor_rekening=str(int(data[index][10].strip())),
                    nomor_npwp=str(int(data[index][11].strip())),
                    alamat_npwp=data[index][12].strip(),
                )
                new_pegawai.save()
            add_log(Account.objects.get(user=self.request.user), "Add Data Pegawai")
            return HttpResponseRedirect(reverse("pegawai:display_pegawai"))
        except Exception as e:
            error_message: str = e.args[0]
            user = self.request.user
            account = Account.objects.get(user=user)

            return TemplateResponse(
                request,
                "add_pegawai_error.html",
                context={"error": error_message, "role": account.role},
                status=400,
            )


class DisplayPegawai(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy(URL_AUTH)
    template_name = "display_pegawai.html"

    def get_template_names(self):
        user = self.request.user
        account = Account.objects.get(user=user)

        if account.role == "Admin":
            template_name = "display_pegawai.html"
        else:
            template_name = FORBIDDEN_PAGE
        return [template_name]

    def get_context_data(self, **kwargs):
        IS_NOT_EMPTY = False
        list_pegawai = (
            Pegawai.objects.all().order_by("employee_no").filter(tombstone=False)
        )
        if len(list_pegawai) != 0:
            IS_NOT_EMPTY = True

        user = self.request.user
        account = Account.objects.get(user=user)

        context = super().get_context_data(**kwargs)
        context["data"] = list_pegawai
        context["isNotEmpty"] = IS_NOT_EMPTY
        context["role"] = account.role

        return context


class UpdatePegawaiView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy(URL_AUTH)

    def get(self, request, *args, **kwargs):
        if len(Pegawai.objects.all()) == 0:
            return HttpResponseRedirect(reverse("pegawai:add_pegawai"))
        return super(UpdatePegawaiView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        user = self.request.user
        account = Account.objects.get(user=user)

        if account.role == "Admin":
            template_name = "update_pegawai.html"
        else:
            template_name = FORBIDDEN_PAGE
        return [template_name]

    def get_context_data(self, **kwargs):
        user = self.request.user
        account = Account.objects.get(user=user)

        context = super().get_context_data(**kwargs)
        context["role"] = account.role
        context["title"] = "Update Employee Data"

        return context


class SaveUpdatePegawai(TemplateView):
    def check_data(self, data: List[List[str]]) -> List:
        unique_email_checker = UniqueEmailInFileChecker(None)
        valid_column_name_checker = ValidColumnNameChecker(unique_email_checker)
        data_cleaner = DataCleaner(valid_column_name_checker)
        return data_cleaner.functionality(data, dict())

    def post(self, request, *args, **kwargs):
        try:
            uploaded_file = request.FILES["file"].read()
            data = convert_to_data(uploaded_file)

            check_data_result = self.check_data(data)
            data = check_data_result[0]
            index_start_data = check_data_result[1]["records_index"]

            self.emails(request, data, index_start_data)

            add_log(Account.objects.get(user=request.user), "Update Data Pegawai")

            return HttpResponseRedirect(reverse("pegawai:display_pegawai"))
        except Exception as e:
            error_message: str = e.args[0]
            user = self.request.user
            account = Account.objects.get(user=user)

            return TemplateResponse(
                request,
                "update_pegawai_error.html",
                context={"error": error_message, "role": account.role},
                status=400,
            )

    def emails(self, request, data, index):
        set_of_emails = set()
        all_pegawais = Pegawai.objects.all()

        for pegawai in all_pegawais:
            set_of_emails.add(pegawai.email)
        for row in range(index, len(data)):
            try:
                email = data[row][7]
                set_of_emails.remove(email)
                if Pegawai.objects.filter(email=email).exists():
                    pegawai = Pegawai.objects.get(email=email)

                    employee_category = data[row][3].strip()
                    self.update_employee_category(pegawai, employee_category)
                    job_status = data[row][4].strip()
                    self.update_job_status(pegawai, job_status)

                    Pegawai.objects.filter(email=email).update(
                        employee_no=str(data[row][1].strip()),
                        employee_name=data[row][2],
                        grade_level=data[row][5],
                        employment_status=data[row][6],
                        nama_di_rekening=data[row][8],
                        nama_bank=data[row][9],
                        nomor_rekening=str(data[row][10].strip()),
                        nomor_npwp=str(data[row][11].strip()),
                        alamat_npwp=data[row][12],
                        tombstone=False,
                    )
            except KeyError:
                new_pegawai = Pegawai(
                    email=data[row][7].strip(),
                    employee_no=str(data[row][1].strip()),
                    employee_name=data[row][2].strip(),
                    employee_category=data[row][3].strip(),
                    job_status=data[row][4].strip(),
                    grade_level=data[row][5].strip(),
                    employment_status=data[row][6].strip(),
                    nama_di_rekening=data[row][8].strip(),
                    nama_bank=data[row][9].strip(),
                    nomor_rekening=str(data[row][10].strip()),
                    nomor_npwp=str(data[row][11].strip()),
                    alamat_npwp=data[row][12].strip(),
                )
                self.update_employee_category(new_pegawai, data[row][3].strip())
                self.update_job_status(new_pegawai, data[row][4].strip())
                new_pegawai.save()

        if len(set_of_emails) > 0:
            for email in set_of_emails:
                Pegawai.objects.filter(email=email).update(tombstone=True)

    def update_employee_category(self, pegawai, employee_category):
        if employee_category == "Lecturer":
            pegawai.employee_category = pegawai.LECTURER
        elif employee_category == "Staff":
            pegawai.employee_category = pegawai.STAFF
        else:
            pegawai.employee_category = pegawai.STAFF
        pegawai.save()

    def update_job_status(self, pegawai, job_status):
        if job_status == "Dosen":
            pegawai.job_status = pegawai.DOSEN
        elif job_status == "Fungsional Tertentu":
            pegawai.job_status = pegawai.FUNGSIONAL_TERTENTU
        elif job_status == "Administrasi":
            pegawai.job_status = pegawai.ADMINISTRASI
        else:
            pegawai.job_status = pegawai.ADMINISTRASI
        pegawai.save()


@require_POST
@login_required(login_url="/login")
def cetak_data_pegawai(request):
    pegawais = Pegawai.objects.all()
    data_pegawai = {
        "header": {
            data_pegawai_cols[0]: data_pegawai_cols[0],
            data_pegawai_cols[1]: data_pegawai_cols[1],
            data_pegawai_cols[2]: data_pegawai_cols[2],
            data_pegawai_cols[3]: data_pegawai_cols[3],
            data_pegawai_cols[4]: data_pegawai_cols[4],
            data_pegawai_cols[5]: data_pegawai_cols[5],
            data_pegawai_cols[6]: data_pegawai_cols[6],
            data_pegawai_cols[7]: data_pegawai_cols[7],
            data_pegawai_cols[8]: data_pegawai_cols[8],
            data_pegawai_cols[9]: data_pegawai_cols[9],
            data_pegawai_cols[10]: data_pegawai_cols[10],
            data_pegawai_cols[11]: data_pegawai_cols[11],
            data_pegawai_cols[12]: data_pegawai_cols[12],
        }
    }

    employee_index = 1
    for pegawai in pegawais:
        data_pegawai[str(pegawai.employee_no)] = {
            data_pegawai_cols[0]: str(employee_index),
            data_pegawai_cols[1]: str(pegawai.employee_no),
            data_pegawai_cols[2]: str(pegawai.employee_name),
            data_pegawai_cols[3]: str(pegawai.employee_category),
            data_pegawai_cols[4]: str(pegawai.job_status),
            data_pegawai_cols[5]: str(pegawai.grade_level),
            data_pegawai_cols[6]: str(pegawai.employment_status),
            data_pegawai_cols[7]: str(pegawai.email),
            data_pegawai_cols[8]: str(pegawai.nama_di_rekening),
            data_pegawai_cols[9]: str(pegawai.nama_bank),
            data_pegawai_cols[10]: str(pegawai.nomor_rekening),
            data_pegawai_cols[11]: str(pegawai.nomor_npwp),
            data_pegawai_cols[12]: str(pegawai.alamat_npwp),
        }
        employee_index += 1

    excel_content = "attachment; filename=data_pegawai.xlsx"
    excel_file = excel_factory("standard").get_excel(data_pegawai)

    response = HttpResponse(
        excel_file.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Dispotition"] = excel_content

    return response
