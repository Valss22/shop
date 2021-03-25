from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from store.decoding import parse_id_token
from store.models import *


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserProductRelationSerializer(ModelSerializer):
    class Meta:
        model = UserProductRelation
        fields = ('product', 'in_cart', 'rate', 'is_rated')


class ProductSerializer(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    reviewers_count = serializers.SerializerMethodField()
    is_rated = serializers.BooleanField(read_only=True, )

    class Meta:
        model = Product
        fields = '__all__'

    def get_reviewers_count(self, instance):
        return UserProductRelation.objects.filter(product=instance, ).count()


class CartProductsSerializer(ModelSerializer):
    class Meta:
        model = CartProduct
        exclude = ('user',)
        depth = 1


class CartSerializer(ModelSerializer):
    products = CartProductsSerializer(read_only=True, many=True)
    unique_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        exclude = ('owner',)

    def get_unique_count(self, instance):
        return Cart.objects.filter(owner=instance.owner).first().products.count()
