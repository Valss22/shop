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

            for i in list(Product.objects.all()):
                Product.objects.filter(id=i.id).update(user=User.objects.get(email=access['email']))

                if UserProductRelation.objects.get(user=User.objects.get(email=access['email']),
                                                   product=Product.objects.get(id=i.id)).in_cart:
                    Product.objects.filter(user=User.objects.get(email=access['email']),
                                           id=i.id).update(in_cart=True)
                else:
                    Product.objects.filter(user=User.objects.get(email=access['email']),
                                           id=i.id).update(in_cart=False)
            return True
        except:
            for i in list(Product.objects.all()):
                Product.objects.filter(id=i.id).update(in_cart=False)
            return True
