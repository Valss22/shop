from rest_framework.pagination import PageNumberPagination
import django_filters
from store.models import *
from store.serializers import *
from django.db.models import Avg

from store.models import UserProductRelation


def set_rating(product):
    rating = UserProductRelation.objects.filter(product=product).aggregate(rating=Avg('rate')).get('rating')
    product.rating = rating
    product.save()
    return rating


def set_like(current_user, pk: int, case: bool) -> Response:
    FeedbackRelation.objects.filter(user=current_user, comment_id=pk).update(like=not case)
    if not case:
        FeedbackRelation.objects.filter(user=current_user, comment_id=pk).update(dislike=case)

    if case:
        likeCount = FeedbackRelation.objects.filter(comment_id=pk, like=case).count()
        dislikeCount = FeedbackRelation.objects.filter(comment_id=pk, dislike=case).count()
    else:
        likeCount = FeedbackRelation.objects.filter(comment_id=pk, like=not case).count()
        dislikeCount = FeedbackRelation.objects.filter(comment_id=pk, dislike=not case).count()

    responce = Response()

    responce.data = {
        'isLiked': not case,
        'likeCount': likeCount,
        'dislikeCount': dislikeCount,
    }
    if not case:
        responce.data['isDisliked'] = False

    return responce


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 21
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CharFilterinField(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = CharFilterinField(field_name='category__name', lookup_expr='in')
    price = django_filters.RangeFilter()
    sale = django_filters.RangeFilter()

    class Meta:
        model = Product
        fields = ['price']
