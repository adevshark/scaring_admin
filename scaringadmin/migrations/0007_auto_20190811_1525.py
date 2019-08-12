# Generated by Django 2.1.11 on 2019-08-11 07:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scaringadmin', '0006_auto_20190811_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitelist',
            name='directory_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='rpassword',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 11, 15, 25, 17, 130818)),
        ),
        migrations.AlterField(
            model_name='sitelist',
            name='scraped_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
