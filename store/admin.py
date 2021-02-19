from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin
from rest_framework.authtoken.models import Token

from store.models import Product, Category, Cart

from django.apps import apps

models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
