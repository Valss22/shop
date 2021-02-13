from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from store.models import Product


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass
