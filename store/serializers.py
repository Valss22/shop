from rest_framework.serializers import ModelSerializer

from store.models import Product


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

