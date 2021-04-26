from django.db.models import Avg

from store.models import *
from rest_framework.response import Response


def get_product(request, parse_id_token, self, ):
    try:
        access = request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        current_user = User.objects.get(email=access['email'])
        instance = self.get_object()
        instance.my_rate = UserProductRelation.objects.get(
            user=current_user,
            product_id=instance.id).rate
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    except UserProductRelation.DoesNotExist:
        instance = self.get_object()
        instance.my_rate = None
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


def set_rating(product: Product):
    rating = UserProductRelation.objects.filter(
        product=product).aggregate(
        rating=Avg('rate')).get('rating')
    product.rating = rating
    product.save()
    return rating
