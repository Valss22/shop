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


class CartProductsSerializer(ModelSerializer):
    copy_price = serializers.SerializerMethodField()

    class Meta:
        model = CartProduct
        exclude = ('user',)
        depth = 1

    def get_copy_price(self, instance):
        return CartProduct.objects.filter(user=instance.user, product=instance.product).first().copy_count * \
               Product.objects.get(id=instance.product.id).price


class ProductRelationSerializer(ModelSerializer):
    info = CartProductsSerializer(read_only=True, )
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)

    class Meta:
        model = UserProductRelation
        exclude = ('user', 'product',)
        depth = 1


class CommentsSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        exclude = ('user',)
        depth = 1


class ProductSerializer(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    reviewers_count = serializers.SerializerMethodField()
    is_rated = serializers.BooleanField(read_only=True, )
    in_cart = serializers.BooleanField(read_only=True, )
    comments = CommentsSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_reviewers_count(self, instance):
        return UserProductRelation.objects.filter(product=instance, ).count()


class CartSerializer(ModelSerializer):
    products = CartProductsSerializer(read_only=True, many=True)
    unique_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'

    def get_unique_count(self, instance):
        return Cart.objects.filter(owner=instance.owner).first().products.count()

    def get_total_price(self, instacne):
        tp = 0
        for i in list(CartProduct.objects.all()):
            if i.user == instacne.owner:
                tp += i.copy_count * i.product.price
        return tp


class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
