import json
from django.contrib.auth.models import User
from djoser.social.token import jwt
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from store.decoding import parse_id_token
from store.models import Product, UserProfile, UserRefreshToken
from store.serializers import ProductsSerializer, MyTokenObtainPairSerializer
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from rest_framework_simplejwt.backends import TokenBackend


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

            # serializer = self.serializer_class(data=request.data)
            # serializer.is_valid(raise_exception=True)
            # data = serializer.validated_data

            try:
                User.objects.get(email=parse_id_token(token['id_token'])['email'])
                refresh = self.serializer_class.get_token(User.objects.get
                                                          (username=parse_id_token(token['id_token'])['name']))

                access = self.serializer_class.get_token(
                    User.objects.get(username=parse_id_token(token['id_token'])['name'])).access_token

                response = Response()
                response.set_cookie(key='refresh', value=str(refresh), httponly=True)
                response.data = {
                    'access': str(access),
                    'email': parse_id_token(token['id_token'])['email'],
                    'name': parse_id_token(token['id_token'])['name'],
                    'picture': parse_id_token(token['id_token'])['picture'],
                }

                try:
                    UserRefreshToken.objects.get(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name']))

                    UserRefreshToken.objects.filter(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name'])).update(refresh=str(refresh))

                except:
                    UserRefreshToken.objects.create(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name']), refresh=refresh)

                try:
                    UserProfile.objects.get(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name']))

                    UserProfile.objects.create(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name']),
                                               picture=parse_id_token(token['id_token'])['picture'])
                except:
                    pass

                return response

            except User.DoesNotExist:
                User.objects.create_user(parse_id_token(token['id_token'])['name'],
                                         parse_id_token(token['id_token'])['email'],
                                         '123')

                refresh = self.serializer_class.get_token(User.objects.get
                                                          (username=parse_id_token(token['id_token'])['name']))

                access = self.serializer_class.get_token(
                    User.objects.get(username=parse_id_token(token['id_token'])['name'])).access_token

                UserRefreshToken.objects.create(user=User.objects.get
                (username=parse_id_token(token['id_token'])['name']), refresh=refresh)

                UserProfile.objects.create(user=User.objects.get
                (username=parse_id_token(token['id_token'])['name']),
                                           picture=parse_id_token(token['id_token'])['picture'])

                response = Response()
                response.set_cookie(key='refresh', value=str(refresh), httponly=True)
                response.data = {
                    'access': str(access),
                    'email': parse_id_token(token['id_token'])['email'],
                    'name': parse_id_token(token['id_token'])['name'],
                    'picture': parse_id_token(token['id_token'])['picture'],
                }

                return response

        except ValueError as err:
            print(err)
            content = {'message': 'Invalid token'}
            return Response(content)


class RefreshTokenView(GenericAPIView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request):
        data = {'token': request.COOKIES['refresh']}

        valid_data = parse_id_token(VerifyJSONWebTokenSerializer().validate(data)['token'])

        try:
            UserRefreshToken.objects.get(user=User.objects.get(id=valid_data['user_id']))

            if UserRefreshToken.objects.get(user=User.objects.get(id=valid_data['user_id'])).refresh == \
                    request.COOKIES['refresh']:
                refresh = self.serializer_class.get_token(User.objects.get(id=valid_data['user_id']))
                access = self.serializer_class.get_token(User.objects.get(id=valid_data['user_id'])).access_token

                UserRefreshToken.objects.filter(user=User.objects.get
                (id=valid_data['user_id'])).update(refresh=str(refresh))

                response = Response()
                response.set_cookie(key='refresh', value=refresh, httponly=True)
                response.data = {
                    'access': str(access),
                    'email': User.objects.get(id=refresh['user_id']).email,
                    'name': User.objects.get(id=refresh['user_id']).username,
                    'picture': UserProfile.objects.get(user=User.objects.get(id=refresh['user_id'])).picture,
                }
                return response
        except:
            return Response({'message': 'Auth failed'})
        else:
            return Response({'message': 'Auth failed'})


class LogoutView(GenericAPIView):

    def post(self, request):
        data = parse_id_token(request.COOKIES['refresh'])['user_id']
        UserRefreshToken.objects.get(user=User.objects.get(id=data)).delete()
        return Response({'message': 'Logout success'})
