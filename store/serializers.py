from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Cart, Category, CartProduct, Product, UserProductRelation


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class UserProductRelationSerializer(ModelSerializer):
    class Meta:
        model = UserProductRelation


class CartProductsSerializer(ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
