import time

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from google.auth.transport import requests
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from store.permissions import *
from google.oauth2 import id_token
from store.services.product import *
from store.services.feedback import *
from store.services.user_profile import *
from store.services.product_relation import *
from store.services.cart import *
from store.services.order import *
from store.services.auth import *
from store.services.filter import *


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all() \
        .annotate(rating=Avg('userproductrelation__rate'), )

    serializer_class = ProductSerializerAll
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = LargeResultsSetPagination
    search_fields = ['name', 'author']
    ordering_fields = ['price', 'author', ]

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ProductSerializerRetrieve
        return get_product(request, parse_id_token, self)


class DiscountProductViewSet(ModelViewSet):
    queryset = Product.objects \
        .filter(sale__gt=0) \
        .annotate(rating=Avg('userproductrelation__rate'), )

    serializer_class = ProductSerializerAll


class UserProductRateView(UpdateModelMixin, GenericViewSet):
    queryset = UserProductRelation.objects.all()
    serializer_class = ProductRelationSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        return get_product_rate(self, parse_id_token)


class UserProductCartView(UpdateModelMixin, GenericViewSet, ):
    queryset = CartProduct.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        return get_product_cart(self, parse_id_token)


class CartViewSet(ModelViewSet):
    permission_classes = [IsAuth]

    def list(self, request, *args, **kwargs):
        return get_cart(self, parse_id_token)


class CartDeleteView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
        return delete_cart(self)


class CartObjView(UpdateModelMixin, GenericViewSet, ):
    queryset = UserProductRelation.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        return decrement_obj_from_cart(self)


class CartDelObjView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
        return delete_obj_from_cart(self, pk)


class FeedbackFormView(APIView):
    permission_classes = [IsAuth]

    def post(self, request, pk):
        return add_feedback(self, request, pk)


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class FeedbackRateCommentView(APIView):
    permission_classes = [IsAuth]

    def patch(self, request, pk):
        return rate_feedback(self, request, set_like, pk)


class UserProfileViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuth]

    def list(self, request, *args, **kwargs):
        return get_user_profile(self)


class UserProfileFormView(APIView):
    permission_classes = [IsAuth]

    def put(self, request):
        return fill_user_profile_form(self, request)


class MakeOrderView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        return make_order(self, request)


class GoogleView(APIView):

    def post(self, request):
        return login(request, id_token)


class RefreshTokenView(APIView):

    def post(self, request):
        return refresh_token(request)


class LogoutView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        return logout(request)
