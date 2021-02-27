from rest_framework.serializers import ModelSerializer

from store.models import Cart, Category, CartProduct, Product


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
