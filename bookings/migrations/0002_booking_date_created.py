# Generated by Django 3.1.4 on 2020-12-29 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='date_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
