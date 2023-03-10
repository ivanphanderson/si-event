# **SI Event (Sistem Informasi Manajemen Event Fasilkom UI)**

Sistem informasi untuk mengelola _events_ di Fasilkom UI dengan memanfaatkan data pegawai yang akan disimpan di sistem ini (ada _constraint_ berupa tidak memungkinkannya pengaksesan data pegawai dari HRIS yang sudah ada). _Role_ yang terlibat dalam penggunaan sistem meliputi Admin (seputar pengelolaan data pegawai dan akun), User (seputar pengelolaan _events_), dan Staf Keuangan (seputar rekapitulasi data keuangan _events_).

## Status _Pipeline_ & Kualitas Kode

### _Master Branch_:

[![pipeline status](https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event/badges/master/pipeline.svg)](https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event/-/commits/master)

### _Staging Branch_:

[![pipeline status](https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event/badges/staging/pipeline.svg)](https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event/-/commits/staging)

### SonarQube & _Coverage_ pada _Production_:

[![Quality Gate Status](https://sonarqube.cs.ui.ac.id/api/project_badges/measure?project=ivan.phanderson_si-event_AYaldJKkYpjyGK7tejy9&metric=alert_status)](https://sonarqube.cs.ui.ac.id/dashboard?id=ivan.phanderson_si-event_AYaldJKkYpjyGK7tejy9)

![coverage](https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event/badges/master/coverage.svg)

## Cara Menjalankan Sistem di _Localhost_ (Untuk _Development_)

**Catatan: Semua _commands_ yang diberikan adalah yang digunakan di OS Windows 11, untuk OS lain mungkin ada penyesuaian, tetapi _flow_-nya tetap sama**

### Prasyarat

Pastikan Python dengan versi < 3.9 (yang digunakan untuk _production_ dan _development_ adalah 3.8.x) dan Git sudah ter-_install_. Lalu, jalankan kode berikut.


```
git clone https://gitlab.cs.ui.ac.id/ivan.phanderson/si-event.git
cd si-event
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

### Mengatur _Environment Variables_

Buat file .env dengan isi sebagai berikut (digunakan _database_ SQLite bawaan Django, jika ingin menggunakan _database_ lain silakan merujuk ke `.\si-event\settings.py` dan sesuaikan isi _file_ berikut).

```
SECRET_KEY='django-insecure-iva@g$r#jof8-m!kzppodser7gudj02kn))^!h(kd&*1cw#q++'

ENVIRONMENT="DEVELOPMENT"
```

### Migrasi Data dan Menjalankan Sistem

Setelah mengatur _environment variables_, selanjutnya lakukan migrasi data dan jalankan sistem dengan menggunakan kode berikut.

```
python manage.py migrate
python manage.py runserver
```
