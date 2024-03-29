# Generated by Django 4.1.3 on 2023-02-20 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_cryptography.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('general_settings', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='Email Address')),
                ('short_name', models.CharField(max_length=30, unique=True, verbose_name='Username')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone')),
                ('is_active', models.BooleanField(default=True, help_text='Important: This controls login access for All staffs and Vendors', verbose_name='Active User')),
                ('is_staff', models.BooleanField(default=False, help_text='Important: This is extra login control for All Staffs only', verbose_name='Permit Staff')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Administrator')),
                ('is_assistant', models.BooleanField(default=False, verbose_name="Admin's Assistant")),
                ('is_stakeholder', models.BooleanField(default=False, help_text='This indicates that the staff is one of the Onboarding members', verbose_name='Onboarding Group')),
                ('is_vendor', models.BooleanField(default=False, help_text='Important: This attribute determine Vendor Admin from their team', verbose_name='Vendor Admin')),
                ('user_type', models.CharField(choices=[('admin', 'Administrator'), ('vendor', 'Vendor, ATM'), ('custodian', 'Custodian, ATM'), ('initiator', 'Member, Onboarding'), ('officer', 'Lead, Onboarding'), ('head', 'Head, Onboarding')], max_length=30, verbose_name='User Type')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Date Joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='Last Login')),
                ('branch', models.ForeignKey(blank=True, help_text='This option is only applicable to staffs', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branch', to='general_settings.branch', verbose_name='Branch or Unit')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('vendor_company', models.ForeignKey(blank=True, help_text='This option is only applicable to vendor type of users', null=True, on_delete=django.db.models.deletion.CASCADE, to='general_settings.vendorcompany', verbose_name='Vendor Company')),
            ],
            options={
                'verbose_name': 'User Manager',
                'verbose_name_plural': 'User Manager',
                'ordering': ('date_joined',),
            },
        ),
        migrations.CreateModel(
            name='TwoFactorAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_code', django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=255, null=True, verbose_name='Access Token'))),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='Last Login')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='twofactorauth', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Access Token',
                'verbose_name_plural': 'Access Token',
                'ordering': ('last_login',),
            },
        ),
    ]
