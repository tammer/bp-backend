# Generated by Django 4.0.4 on 2022-07-12 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_anchor_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='endorsement',
            name='anchor',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.anchor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='anchor',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('accepted', 'accepted'), ('declined', 'declined'), ('expired', 'expired'), ('cancelled', 'cancelled')], default='pending', max_length=120),
        ),
    ]
