# Generated by Django 3.1.6 on 2021-03-31 10:44

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0074_auto_20210331_1357'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedbackrelation',
            name='product',
        ),
        migrations.AddField(
            model_name='feedbackrelation',
            name='comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='store.feedback'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 3, 31, 16, 44, 13, 147231)),
        ),
    ]
