# Generated by Django 3.1.6 on 2021-02-13 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
    ]