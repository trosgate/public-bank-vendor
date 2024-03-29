# Generated by Django 4.1.3 on 2023-02-24 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0014_remove_application_states_alter_panelist_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='panelist',
            name='meeting_link',
            field=models.URLField(blank=True, max_length=2048, null=True, verbose_name='Meeting Link'),
        ),
        migrations.AlterField(
            model_name='panelist',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='External Panelist Name'),
        ),
    ]
