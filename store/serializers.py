from django.contrib.auth.models import User
from django.db.models import Avg, F
from django.http import HttpRequest
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
    copyDiscountPrice = serializers.SerializerMethodField()

    class Meta:
        model = CartProduct
        exclude = ('user',)
        depth = 1

    def get_copy_price(self, instance):
        return CartProduct.objects.get(user=instance.user, product=instance.product).copy_count * \
               Product.objects.get(id=instance.product.id).price

    def get_copyDiscountPrice(self, instance):
        discountPrice = Product.objects.get(id=instance.product.id).discountPrice
        if discountPrice == None:
            return None
        return CartProduct.objects.get(user=instance.user, product=instance.product).copy_count * discountPrice


class ProductRelationSerializer(ModelSerializer):
    rating = serializers.SerializerMethodField()
    reviewersCount = serializers.SerializerMethodField()

    class Meta:
        model = UserProductRelation
        exclude = ('user', 'product',)
        depth = 1

    def get_rating(self, instance):
        avg = 0
        for i in list(UserProductRelation.objects.filter(product=instance.product)):
            if type(i.rate) == int:
                avg += i.rate
        avg /= len(UserProductRelation.objects.filter(product=instance.product))
        return avg

    def get_reviewersCount(self, instance):
        return UserProductRelation.objects.filter(product=instance.product, ).count()


class CommentsSerializer(ModelSerializer):
    likeCount = serializers.SerializerMethodField()
    dislikeCount = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    isDisliked = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        exclude = ('user',)
        depth = 1

    def get_likeCount(self, instance):
        return FeedbackRelation.objects.filter(comment_id=instance.id, like=True).count()

    def get_dislikeCount(self, instance):
        return FeedbackRelation.objects.filter(comment_id=instance.id, dislike=True).count()

    def get_isLiked(self, instance):
        try:
            access = self.context.get('request', None).headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            currentUser = User.objects.get(email=access['email'])
            try:
                FeedbackRelation.objects.get(user=currentUser, comment_id=instance.id)

                if FeedbackRelation.objects.get(user=currentUser, comment_id=instance.id).like:
                    return True
                return False
            except:
                return False
        except:
            return False

    def get_isDisliked(self, instance):
        try:
            access = self.context.get('request', None).headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            currentUser = User.objects.get(email=access['email'])
            try:
                FeedbackRelation.objects.get(user=currentUser, comment_id=instance.id)

                if FeedbackRelation.objects.get(user=currentUser, comment_id=instance.id).dislike:
                    return True
                return False
            except:
                return False
        except:
            return False


class ProductSerializer(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    my_rate = serializers.IntegerField(max_value=5, read_only=True)
    reviewers_count = serializers.SerializerMethodField()
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
    totalDiscountPrice = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'

    def get_unique_count(self, instance):
        return Cart.objects.filter(owner=instance.owner).first().products.count()

    def get_total_price(self, instacne):
        tp = 0
        for i in list(CartProduct.objects.filter(user=instacne.owner)):
            tp += i.copy_count * i.product.price
        return tp

    def get_totalDiscountPrice(self, instance):
        tdp = 0
        count = 0
        arr = list(CartProduct.objects.filter(user=instance.owner))
        for i in arr:
            if i.product.discountPrice == None:
                continue
            tdp += i.copy_count * i.product.discountPrice
            if i.product.sale == None:
                count += 1
        if count == len(arr):
            return None
        return tdp


class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class FeedbackRelationSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
