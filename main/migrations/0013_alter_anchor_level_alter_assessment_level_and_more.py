# Generated by Django 4.0.4 on 2022-07-10 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_anchor_unique_together_anchor_receiver_invite_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anchor',
            name='level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='level',
            field=models.IntegerField(),
        ),
        migrations.DeleteModel(
            name='Level',
        ),
    ]
