from django.contrib.auth.models import User
from djoser.social.token import jwt
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView
from store.decoding import parse_id_token
from store.models import Product, UserProfile
from store.serializers import ProductsSerializer, MyTokenObtainPairSerializer
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer


class GoogleView(GenericAPIView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request):
        token = {'id_token': request.data.get('id_token')}

        try:
            idinfo = id_token.verify_oauth2_token(token['id_token'],
                                                  requests.Request(), config('googleClientId'))

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            try:
                User.objects.get(email=parse_id_token(token['id_token'])['email'])
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data
                return Response(data, status=status.HTTP_200_OK)

            except ValueError:
                User.objects.create_user(parse_id_token(token['id_token'])['name'],
                                         parse_id_token(token['id_token'])['email'],
                                         '123')

                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data
                return Response(data, status=status.HTTP_200_OK)

        except ValueError as err:
            print(err)
            content = {'message': 'Invalid token'}
            return Response(content)
