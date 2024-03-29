# Generated by Django 4.1.3 on 2023-02-23 00:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0009_parameters_modified_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grading',
            name='marks1',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 1'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='marks2',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 2'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='marks3',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 3'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='marks4',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 4'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='marks5',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 5'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='marks6',
            field=models.PositiveIntegerField(choices=[(1, '1 Mark'), (2, '2 Marks'), (3, '3 Marks'), (4, '4 Marks'), (5, '5 Marks')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Marks 6'),
        ),
    ]
