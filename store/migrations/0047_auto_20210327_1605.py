# Generated by Django 3.1.6 on 2021-03-27 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0046_product_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='comments',
        ),
        migrations.AddField(
            model_name='product',
            name='comments',
            field=models.ManyToManyField(null=True, to='store.Feedback'),
        ),
    ]