from django.db.models import F

from store.models import *


def get_product_rate(self, parse_id_token, ):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    current_user = User.objects.get(email=access['email'])

    CartProduct.objects.get_or_create(
        user=current_user,
        product=Product.objects.get(
            id=self.kwargs['book'])
    )
    obj, created = UserProductRelation.objects.get_or_create(
        user=current_user,
        product_id=self.kwargs['book']
    )
    obj.is_rated = True
    obj.save()
    return obj


def get_product_cart(self, parse_id_token):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    current_user = User.objects.get(email=access['email'])
    current_product = Product.objects.get(id=self.kwargs['book'])

    CartProduct.objects.get_or_create(
        user=current_user,
        product=current_product
    )
    CartProduct.objects.filter(
        user=current_user,
        product=current_product).update(
        copy_count=F('copy_count') + 1
    )
    Cart.objects.get_or_create(owner=current_user)
    Cart.objects.filter(
        owner=current_user).first().products.add(
        CartProduct.objects.filter(
            user=current_user
        ).last()
    )
    obj, created = CartProduct.objects.get_or_create(
        user=current_user,
        product=current_product
    )
    return obj
