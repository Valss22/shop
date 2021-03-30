# Generated by Django 3.1.6 on 2021-03-30 14:03

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0070_auto_20210330_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 3, 30, 20, 3, 45, 126587)),
        ),
        migrations.AlterField(
            model_name='userproductrelation',
            name='info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.cartproduct'),
        ),
        migrations.AlterField(
            model_name='userproductrelation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
