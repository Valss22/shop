# Generated by Django 3.1.6 on 2021-03-30 09:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0066_auto_20210330_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 3, 30, 15, 49, 20, 300110)),
        ),
    ]