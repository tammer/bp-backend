# Generated by Django 4.0.4 on 2022-06-24 16:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0007_assessment'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together={('owner', 'skill')},
        ),
    ]
