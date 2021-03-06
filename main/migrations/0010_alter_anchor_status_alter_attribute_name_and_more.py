# Generated by Django 4.0.4 on 2022-06-30 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_assessment_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anchor',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('active', 'active'), ('declined', 'declined'), ('expired', 'expired'), ('canceled', 'canceled')], default='pending', max_length=120),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='level',
            name='name',
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
