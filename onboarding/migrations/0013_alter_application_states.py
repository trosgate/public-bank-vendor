# Generated by Django 4.1.3 on 2023-02-23 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0012_alter_application_states'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='states',
            field=models.CharField(choices=[('accept', 'Approve Vendor'), ('reject', 'Reject Vendor')], max_length=20, verbose_name='State'),
        ),
    ]
