# Generated by Django 4.1.3 on 2023-02-22 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0008_parameters_reference_alter_parameters_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameters',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Created'),
        ),
    ]
