from django.db import models


class Pegawai(models.Model):
    STAFF = 'S'
    LECTURER = 'L'
    DOSEN = 'D'
    ADMINISTRASI = 'A'
    FUNGSIONAL_TERTENTU = 'FT'

    EMPLOYEE_CATEGORY_CHOICES = [
        (STAFF, 'Staff'),
        (LECTURER, 'Lecturer'),
    ]

    JOB_STATUS_CHOICES = [
        (DOSEN, 'Dosen'),
        (ADMINISTRASI, 'Administrasi'),
        (FUNGSIONAL_TERTENTU, 'Fungsional Tertentu'),
    ]

    email = models.EmailField(primary_key=True)
    employee_no = models.CharField(max_length=18)
    employee_name = models.CharField(max_length=50)
    employee_category = models.CharField(max_length=50, choices=EMPLOYEE_CATEGORY_CHOICES, default=STAFF)
    job_status = models.CharField(max_length=50, choices=JOB_STATUS_CHOICES, default=ADMINISTRASI)
    grade_level = models.CharField(max_length=10, default='-')
    employment_status = models.CharField(max_length=50)
    nama_di_rekening = models.CharField(max_length=50)
    nama_bank = models.CharField(max_length=50)
    nomor_rekening = models.CharField(max_length=50)
    nomor_npwp = models.CharField(max_length=20)
    alamat_npwp = models.CharField(max_length=200)
    tombstone = models.BooleanField(default=False)
