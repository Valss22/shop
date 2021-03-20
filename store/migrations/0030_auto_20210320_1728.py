# Generated by Django 3.1.6 on 2021-03-20 11:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0029_auto_20210228_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='UserProductRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_cart', models.BooleanField(default=False)),
                ('rate', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Terribly'), (2, 'Bad'), (3, 'Fine'), (4, 'Good'), (5, 'Amazing')], null=True)),
                ('is_rated', models.BooleanField(blank=True, default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='reviewers',
            field=models.ManyToManyField(through='store.UserProductRelation', to=settings.AUTH_USER_MODEL),
        ),
    ]
