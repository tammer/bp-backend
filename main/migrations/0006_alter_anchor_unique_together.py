# Generated by Django 4.0.4 on 2022-06-22 23:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0005_alter_anchor_receiver'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='anchor',
            unique_together={('passer', 'receiver_email', 'skill')},
        ),
    ]
