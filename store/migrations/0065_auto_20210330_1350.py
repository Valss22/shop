# Generated by Django 3.1.6 on 2021-03-30 07:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0064_auto_20210330_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 3, 30, 13, 50, 34, 851906)),
        ),
    ]
