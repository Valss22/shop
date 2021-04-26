from django.db.models import F
from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def get_cart(self, parse_id_token):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    try:
        queryset = Cart.objects.get(owner=User.objects.get(email=access['email']))
    except Cart.DoesNotExist:
        return Response([], status=status.HTTP_204_NO_CONTENT)
    serializer = CartSerializer(queryset, )
    return Response(serializer.data)


def delete_cart(self, ):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])

    if len(list(CartProduct.objects.filter(user=currentUser))) > 0:
        CartProduct.objects.filter(user=currentUser).delete()
        Cart.objects.filter(owner=currentUser).delete()
        return Response({"message": "Cart deleted success"},
                        status.HTTP_200_OK)
    else:
        return Response({"message": "Cart is empty"},
                        status.HTTP_204_NO_CONTENT)


def decrement_obj_from_cart(self, ):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])
    currentProduct = Product.objects.get(id=self.kwargs['book'])

    if CartProduct.objects.filter(user=currentUser,
                                  product=currentProduct) \
            .first().copy_count == 1:
        obj = CartProduct.objects.get(user=currentUser,
                                      product_id=self.kwargs['book'])
        return obj
    else:
        CartProduct.objects.filter(
            user=currentUser,
            product=currentProduct).update(
            copy_count=F('copy_count') - 1
        )
        obj = CartProduct.objects.get(user=currentUser, product_id=self.kwargs['book'])
        return obj


def delete_obj_from_cart(self, pk):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])
    currentProduct = Product.objects.get(id=pk)

    try:
        CartProduct.objects.get(
            user=currentUser,
            product=currentProduct
        )
        CartProduct.objects.filter(
            user=currentUser,
            product=currentProduct
        ).delete()

        inst = CartSerializer()
        cart = Cart.objects.filter(owner=currentUser).first()

        if CartSerializer.get_totalCount(inst, cart) == 0:
            Cart.objects.filter(owner=currentUser).delete()

        return Response({'message': 'book successfully deleted'},
                        status.HTTP_200_OK)
    except CartProduct.DoesNotExist:
        return Response({'message': '''book doesn't exists'''},
                        status.HTTP_204_NO_CONTENT)
