from django.db.models import F

from store.models import *


def get_product_rate(self, parse_id_token, ):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])

    CartProduct.objects.get_or_create(
        user=currentUser,
        product=Product.objects.get(
            id=self.kwargs['book'])
    )
    obj, created = UserProductRelation.objects.get_or_create(
        user=currentUser,
        product_id=self.kwargs['book']
    )
    obj.is_rated = True
    obj.save()
    return obj


def get_product_cart(self, parse_id_token):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])
    currentProduct = Product.objects.get(id=self.kwargs['book'])

    CartProduct.objects.get_or_create(
        user=currentUser,
        product=currentProduct
    )
    CartProduct.objects.filter(
        user=currentUser,
        product=currentProduct).update(
        copy_count=F('copy_count') + 1
    )
    Cart.objects.get_or_create(owner=currentUser)
    Cart.objects.filter(
        owner=currentUser).first().products.add(
        CartProduct.objects.filter(
            user=currentUser
        ).last()
    )
    obj, created = CartProduct.objects.get_or_create(
        user=currentUser,
        product=currentProduct
    )
    return obj
