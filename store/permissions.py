import jwt
from jwt import InvalidSignatureError
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response

from shop import settings


class IsAuth(BasePermission):
    def has_permission(self, request, view):
        try:
            access = request.headers['Authorization'].split(' ')[1]
            jwt.decode(access, settings.ACCESS_SECRET_KEY)
            return True
        except:
            return False
