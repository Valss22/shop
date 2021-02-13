from rest_framework.viewsets import ModelViewSet

from store.models import Product
from store.serializers import ProductsSerializer


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer

