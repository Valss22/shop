from rest_framework import serializers
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
        exclude = ('description', 'category',
                   'reviewers', 'comments')


class CartProductsSerializer(ModelSerializer):
    copy_price = serializers.SerializerMethodField()
    copy_discount_price = serializers.SerializerMethodField()
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

    def get_copy_discount_price(self, instance):
        discount_price = Product.objects.get(
            id=instance.product.id).discountPrice
        if discount_price is None:
            return None

        cd = CartProduct.objects.get(
            user=instance.user,
            product=instance.product
        ).copy_count * discount_price

        CartProduct.objects.filter(
            user=instance.user,
            product=instance.product).update(
            copyDiscountPrice=cd
        )
        return cd


class ProductRelationSerializer(ModelSerializer):
    rating = serializers.SerializerMethodField()
    reviewers_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProductRelation
        exclude = ('user', 'product',)
        depth = 1

    def get_rating(self, instance):
        avg = 0
        for i in list(UserProductRelation.objects.filter(
                product=instance.product)):
            if type(i.rate) == int:
                avg += i.rate

        avg /= len(UserProductRelation.objects.filter(
            product=instance.product)
        )
        return avg

    def get_reviewers_count(self, instance):
        return UserProductRelation.objects.filter(
            product=instance.product,
        ).count()


class CommentsSerializer(ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        exclude = ('user',)
        depth = 1

    def get_like_count(self, instance):
        return FeedbackRelation.objects.filter(
            comment_id=instance.id, like=True).count()

    def get_dislike_count(self, instance):
        return FeedbackRelation.objects.filter(
            comment_id=instance.id, dislike=True
        ).count()

    def get_is_liked(self, instance):
        try:
            access = self.context.get('request', None) \
                .headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            currentUser = User.objects.get(email=access['email'])
            try:
                fb_obj = FeedbackRelation.objects \
                    .get(user=currentUser,
                         comment_id=instance.id)
                if fb_obj.like:
                    return True
                return False
            except FeedbackRelation.DoesNotExist:
                return False
        except:
            return False

    def get_is_disliked(self, instance):
        try:
            access = self.context.get('request', None) \
                .headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            current_user = User.objects.get(email=access['email'])
            try:
                fb_obj = FeedbackRelation.objects\
                    .get(user=current_user,
                         comment_id=instance.id)
                if fb_obj.dislike:
                    return True
                return False
            except FeedbackRelation.DoesNotExist:
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
    total_price = serializers.SerializerMethodField()
    total_discount_price = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        exclude = ('owner',)

    def get_total_count(self, instance):
        tc = 0
        for i in list(CartProduct.objects.filter(user=instance.owner)):
            tc += i.copy_count
        return tc

    def get_total_price(self, instacne):
        tp = 0
        for i in list(CartProduct.objects.filter(user=instacne.owner)):
            tp += i.copy_count * i.product.price
        return tp

    def get_total_discount_price(self, instance):
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


class OrderProductSerializer(ModelSerializer):
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
