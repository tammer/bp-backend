# Generated by Django 4.0.4 on 2022-07-22 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_job_opportunity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='spec',
            field=models.JSONField(),
        ),
    ]
