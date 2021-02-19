from rest_framework.serializers import ModelSerializer

from store.models import Product, Cart, Category, CartProduct

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartProductsSerializer(ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
