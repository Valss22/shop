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
