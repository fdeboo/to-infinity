# Generated by Django 3.1.3 on 2020-11-24 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='email',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='last_name',
        ),
    ]
