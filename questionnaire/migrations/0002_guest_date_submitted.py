# Generated by Django 4.2.20 on 2025-04-02 17:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='date_submitted',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
