from django.http import HttpResponseRedirect
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


class AddPegawaiView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('authentication:login')
    template_name = "add_pegawai.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        account = Account.objects.get(user=user)
        if account.role == 'Admin':
            return super(AddPegawaiView, self).get(request, *args, **kwargs)


class SavePegawaiToDatabase(CreateView):

    def check_data(
        self, 
        data: List[List[str]]
    ) -> List:
        unique_email_checker = UniqueEmailInFileChecker(None)
        valid_column_name_checker = ValidColumnNameChecker(unique_email_checker)
        data_cleaner = DataCleaner(valid_column_name_checker)
        return data_cleaner.functionality(data, dict())

    def post(self, request, *args, **kwargs):
        try:
            bytes_file = request.FILES['file'].read()
            data: List[List[str]] = convert_to_data(bytes_file)

            check_data_result = self.check_data(data)
            data = check_data_result[0]
            index_start_data = check_data_result[1]['records_index']

            for index in range(index_start_data, len(data)):
                new_pegawai = Pegawai(
                    email = data[index][7].strip(),
                    employee_no = str(int(data[index][1].strip())),
                    employee_name = data[index][2].strip(),
                    employee_category = data[index][3].strip(),
                    job_status = data[index][4].strip(),
                    grade_level = data[index][5].strip(),
                    employment_status = data[index][6].strip(),
                    nama_di_rekening = data[index][8].strip(),
                    nama_bank = data[index][9].strip(),
                    nomor_rekening = str(int(data[index][10].strip())),
                    nomor_npwp = str(int(data[index][11].strip())),
                    alamat_npwp = data[index][12].strip(),
                )
                new_pegawai.save()
            add_log(Account.objects.get(user=self.request.user), 'Add Data Pegawai')
            return HttpResponseRedirect(reverse('pegawai:display_pegawai'))
        except Exception as e:
            error_message: str = e.args[0]
            return TemplateResponse(
                request,
                'add_pegawai_error.html', 
                context={'error': error_message}, 
                status=400,
            )


class DisplayPegawaiView(TemplateView):
    template_name = "display_pegawai.html"
    
    def get_context_data(self, **kwargs):
        IS_NOT_EMPTY = False
        list_pegawai = Pegawai.objects.all().order_by('employee_no')
        if len(list_pegawai) != 0:
            IS_NOT_EMPTY = True
      
        context = super().get_context_data(**kwargs)
        context['data'] = list_pegawai  
        context['isNotEmpty'] = IS_NOT_EMPTY
        
        return context
    
class UpdatePegawaiView(TemplateView):
    login_url = reverse_lazy('authentication:login')
    template_name = "update_pegawai.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        account = Account.objects.get(user=user)
        if account.role == 'Admin':
            return super(UpdatePegawaiView, self).get(request, *args, **kwargs)

class SaveUpdatePegawai(TemplateView):

    def check_data(
        self, 
        data: List[List[str]]
    ) -> List:
        unique_email_checker = UniqueEmailInFileChecker(None)
        valid_column_name_checker = ValidColumnNameChecker(unique_email_checker)
        data_cleaner = DataCleaner(valid_column_name_checker)
        return data_cleaner.functionality(data, dict())
    
    def post(self, request, *args, **kwargs):
        try:
            uploaded_file = request.FILES['file'].read()
            data = convert_to_data(uploaded_file)

            check_data_result = self.check_data(data)
            data = check_data_result[0]
            index_start_data = check_data_result[1]['records_index']

            self.emails(request, data, index_start_data)
            return HttpResponseRedirect(reverse('pegawai:display_pegawai'))
        except Exception as e:
            error_message: str = e.args[0]
            print("masuk sini", error_message)
            print(e)
            return TemplateResponse(
                request,
                'update_pegawai_error.html', 
                context={'error': error_message}, 
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
                        employee_no= str(data[row][1].strip()), employee_name=data[row][2],
                        grade_level = data[row][5], employment_status = data[row][6],
                        nama_di_rekening = data[row][8], nama_bank = data[row][9],
                        nomor_rekening = str(data[row][10].strip()), nomor_npwp = str(data[row][11].strip()),
                        alamat_npwp = data[row][12], tombstone = False
                    )
            except KeyError:
                new_pegawai = Pegawai(
                    email = data[row][7].strip(), employee_no = str(data[row][1].strip()),
                    employee_name = data[row][2].strip(), employee_category = data[row][3].strip(),
                    job_status = data[row][4].strip(), grade_level = data[row][5].strip(),
                    employment_status = data[row][6].strip(), nama_di_rekening = data[row][8].strip(),
                    nama_bank = data[row][9].strip(), nomor_rekening = str(data[row][10].strip()),
                    nomor_npwp = str(data[row][11].strip()), alamat_npwp = data[row][12].strip(),
                )
                self.update_employee_category(new_pegawai, data[row][3].strip())
                self.update_job_status(new_pegawai, data[row][4].strip())
                new_pegawai.save()

        if len(set_of_emails) > 0:
            for email in set_of_emails:
                Pegawai.objects.filter(email=email).update(tombstone=True)

    def update_employee_category(self, pegawai, employee_category):
        if employee_category == 'Lecturer':
            pegawai.employee_category = pegawai.LECTURER
        elif employee_category == 'Staff':
            pegawai.employee_category = pegawai.STAFF 
        else:
            pegawai.employee_category = pegawai.STAFF
        pegawai.save()
    
    def update_job_status(self, pegawai, job_status):
        if job_status == 'Dosen':
            pegawai.job_status = pegawai.DOSEN
        elif job_status == 'Fungsional Tertentu':
            pegawai.job_status = pegawai.FUNGSIONAL_TERTENTU
        elif job_status == 'Administrasi':
            pegawai.job_status = pegawai.ADMINISTRASI
        else:
            pegawai.job_status = pegawai.ADMINISTRASI
        pegawai.save()