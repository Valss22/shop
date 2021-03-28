import jwt
from django.contrib.auth.models import User
from django.db.models import F
from rest_framework.permissions import BasePermission

from shop import settings
from store.decoding import parse_id_token
from store.models import *


class IsAuth(BasePermission):
    def has_permission(self, request, view) -> bool:
        try:
            access = request.headers['Authorization'].split(' ')[1]
            jwt.decode(access, settings.ACCESS_SECRET_KEY, algorithms='HS256')
            return True
        except:
            return False


class FixInCart(BasePermission):
    def has_permission(self, request, view) -> bool:
        try:
            access = request.headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            Product.objects.all().update(user=User.objects.get(email=access['email']))
            for i in list(CartProduct.objects.all()):
                if CartProduct.objects.get(user=User.objects.get(email=access['email']),
                                           product=i.product).in_cart:
                    Product.objects.filter(user=User.objects.get(email=access['email']),
                                           id=i.product.id).update(in_cart=True)

            # for i in list(Product.objects.all()):
            #     Product.objects.filter(id=i.id).update(user=User.objects.get(email=access['email']))
            #
            #     if UserProductRelation.objects.get(user=User.objects.get(email=access['email']),
            #                                        product=Product.objects.get(id=i.id)).in_cart:
            #         Product.objects.filter(user=User.objects.get(email=access['email']),
            #                                id=i.id).update(in_cart=True)
            #         print(111111111111)
            #     else:
            #         print(2222222222)
            #         Product.objects.filter(user=User.objects.get(email=access['email']),
            #                                id=i.id).update(in_cart=False)
            return True
        except:
            # for i in list(Product.objects.all()):
            #     Product.objects.filter(id=i.id).update(in_cart=False)
            Product.objects.all().update(user=None, in_cart=False)
            return True
