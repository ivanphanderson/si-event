# Generated by Django 3.1.3 on 2023-04-25 13:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth_sso', '0001_initial'),
        ('account', '0002_account_is_first_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_first_login',
        ),
        migrations.AddField(
            model_name='account',
            name='accSSO',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth_sso.ssouiaccount'),
        ),
        migrations.AddField(
            model_name='account',
            name='accountType',
            field=models.CharField(choices=[('Non SSO UI', 'Non SSO UI'), ('SSO UI', 'SSO UI')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='account',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='account',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('User', 'User'), ('Staff Keuangan', 'Staff Keuangan'), ('Guest', 'Guest')], max_length=20),
        ),
        migrations.CreateModel(
            name='NonSSOAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='', max_length=150)),
                ('email', models.EmailField(default='', max_length=254)),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('User', 'User'), ('Staff Keuangan', 'Staff Keuangan'), ('Guest', 'Guest')], max_length=20)),
                ('is_first_login', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='accNonSSO',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.nonssoaccount'),
        ),
    ]
