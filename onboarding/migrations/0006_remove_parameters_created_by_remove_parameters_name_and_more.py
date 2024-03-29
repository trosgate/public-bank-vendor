# Generated by Django 4.1.3 on 2023-02-22 19:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onboarding', '0005_remove_grading_approved_by_remove_grading_criteria10_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameters',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='parameters',
            name='name',
        ),
        migrations.RemoveField(
            model_name='parameters',
            name='preview',
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria1',
            field=models.CharField(default='Criteria 1', max_length=100, verbose_name='Criteria 1'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria2',
            field=models.CharField(default='Criteria 2', max_length=100, verbose_name='Criteria 2'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria3',
            field=models.CharField(default='Criteria 3', max_length=100, verbose_name='Criteria 3'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria4',
            field=models.CharField(default='Criteria 4', max_length=100, verbose_name='Criteria 4'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria5',
            field=models.CharField(default='Criteria 5', max_length=100, verbose_name='Criteria 5'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='criteria6',
            field=models.CharField(default='Criteria 6', max_length=100, verbose_name='Criteria 6'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='paramcreator', to=settings.AUTH_USER_MODEL, verbose_name='Last Editor'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note1',
            field=models.CharField(default='Criteria 1 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 1'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note2',
            field=models.CharField(default='Criteria 2 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 2'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note3',
            field=models.CharField(default='Criteria 3 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 3'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note4',
            field=models.CharField(default='Criteria 4 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 4'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note5',
            field=models.CharField(default='Criteria 5 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 5'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='note6',
            field=models.CharField(default='Criteria 6 note', help_text='What information does this parameter seek to find from vendors. This will guide but not restrict Panelists.', max_length=350, verbose_name='Guiding Note 6'),
        ),
    ]
