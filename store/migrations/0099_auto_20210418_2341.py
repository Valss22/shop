# Generated by Django 3.1.6 on 2021-04-18 17:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0098_auto_20210418_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='orderProducts',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 4, 18, 23, 41, 3, 432586)),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 4, 18, 23, 41, 3, 436585)),
        ),
    ]
