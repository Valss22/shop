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


class ProductForCartProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        exclude = ('description', 'category', 'reviewers', 'comments')


class CartProductsSerializer(ModelSerializer):
    copy_price = serializers.SerializerMethodField()
    copyDiscountPrice = serializers.SerializerMethodField()
    product = ProductForCartProductSerializer(read_only=True)

    class Meta:
        model = CartProduct
        exclude = ('user', 'copyPrice',)
        depth = 1

    def get_copy_price(self, instance):
        cp = CartProduct.objects.get(
            user=instance.user,
            product=instance.product).copy_count * \
             Product.objects.get(
                 id=instance.product.id
             ).price
        CartProduct.objects.filter(
            user=instance.user,
            product=instance.product).update(
            copyPrice=cp
        )
        return cp

    def get_copyDiscountPrice(self, instance):
        discountPrice = Product.objects.get(id=instance.product.id).discountPrice
        if discountPrice is None:
            return None
        cd = CartProduct.objects.get(
            user=instance.user,
            product=instance.product
        ).copy_count * discountPrice
        CartProduct.objects.filter(
            user=instance.user,
            product=instance.product).update(
            copyDiscountPrice=cd
        )
        return cd


class ProductRelationSerializer(ModelSerializer):
    rating = serializers.SerializerMethodField()
    reviewersCount = serializers.SerializerMethodField()

    class Meta:
        model = UserProductRelation
        exclude = ('user', 'product',)
        depth = 1

    def get_rating(self, instance):
        avg = 0
        for i in list(UserProductRelation.objects.filter(
                product=instance.product)
        ):
            if type(i.rate) == int:
                avg += i.rate

        avg /= len(UserProductRelation.objects.filter(
            product=instance.product)
        )
        return avg

    def get_reviewersCount(self, instance):
        return UserProductRelation.objects.filter(
            product=instance.product,
        ).count()


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
        return FeedbackRelation.objects.filter(
            comment_id=instance.id, like=True).count()

    def get_dislikeCount(self, instance):
        return FeedbackRelation.objects.filter(
            comment_id=instance.id, dislike=True
        ).count()

    def get_isLiked(self, instance):
        try:
            access = self.context.get('request', None).headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            currentUser = User.objects.get(email=access['email'])
            try:
                FeedbackRelation.objects.get(user=currentUser,
                                             comment_id=instance.id)
                if FeedbackRelation.objects.get(user=currentUser,
                                                comment_id=instance.id).like:
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


class ProductSerializerAll(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    my_rate = serializers.IntegerField(max_value=5, read_only=True)
    in_cart = serializers.BooleanField(read_only=True, )

    class Meta:
        model = Product
        exclude = ('comments', 'description', 'reviewers',)


class ProductSerializerRetrieve(ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, read_only=True, default=0)
    my_rate = serializers.IntegerField(max_value=5, read_only=True)
    reviewers_count = serializers.SerializerMethodField()
    in_cart = serializers.BooleanField(read_only=True, )

    comments = CommentsSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        exclude = ('reviewers',)

    def get_reviewers_count(self, instance):
        return UserProductRelation.objects.filter(product=instance, ).count()


class CartSerializer(ModelSerializer):
    products = CartProductsSerializer(read_only=True, many=True)
    # unique_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    totalDiscountPrice = serializers.SerializerMethodField()
    totalCount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        exclude = ('owner',)

    def get_totalCount(self, instance):
        tc = 0
        for i in list(CartProduct.objects.filter(user=instance.owner)):
            tc += i.copy_count
        # Cart.objects.filter(owner=instance.owner).update(totalCount=tc)
        return tc

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
            if i.product.discountPrice is None:
                tdp += i.copy_count * i.product.price
            else:
                tdp += i.copy_count * i.product.discountPrice
            if i.product.sale is None:
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


class ProductForCopyProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'author', 'image')


class CopyProductSerializer(ModelSerializer):
    product = ProductForCopyProductSerializer(read_only=True)

    class Meta:
        model = CopyProduct
        exclude = ('user',)
        depth = 1


class OrderProductSerializer(ModelSerializer):
    products = CopyProductSerializer(many=True, read_only=True)

    class Meta:
        model = OrderProduct
        exclude = ('user',)
        depth = 2


class OrderDataSerializer(ModelSerializer):
    class Meta:
        model = OrderData
        exclude = ('user', 'id')


class UserProfileSerializer(ModelSerializer):
    orderData = OrderDataSerializer(read_only=True)
    orderItems = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        exclude = ('id', 'user',)


class UserPhotoProfileSerializer(ModelSerializer):
    class Meta:
        model = UserPhotoProfile
        exclude = ('user',)
