from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from store.decoding import parse_id_token
from store.models import Cart, Category, CartProduct, Product, UserProductRelation


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserProductRelationSerializer(ModelSerializer):
    class Meta:
        model = UserProductRelation
        fields = ('product', 'in_cart', 'rate', 'is_rated')

    # def validate(self, attrs):
    #     if len(attrs) == 1:
    #         try:
    #             var = attrs['rate']
    #             return attrs
    #         except:
    #             raise Exception
    #     else:
    #         return False


class ProductSerializer(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    reviewers_count = serializers.SerializerMethodField()
    in_cart = serializers.BooleanField(read_only=True,)
    is_rated = serializers.BooleanField(read_only=True,)

    class Meta:
        model = Product
        fields = '__all__'

    def get_reviewers_count(self, instance):
        return UserProductRelation.objects.filter(product=instance, ).count()


class CartProductsSerializer(ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
