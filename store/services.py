from rest_framework.pagination import PageNumberPagination
import django_filters
from store.models import Product
from django.db.models import Avg

from store.models import UserProductRelation


def set_rating(product):
    rating = UserProductRelation.objects.filter(product=product).aggregate(rating=Avg('rate')).get('rating')
    product.rating = rating
    product.save()
    return rating


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 21
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CharFilterinField(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = CharFilterinField(field_name='category__name', lookup_expr='in')
    price = django_filters.RangeFilter()

    class Meta:
        model = Product
        fields = ['price']
