# Generated by Django 3.1.6 on 2021-02-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_auto_20210220_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.CharField(max_length=500),
        ),
    ]