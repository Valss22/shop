import time
from django.contrib.auth.models import User
import jwt
from django.db.models import Avg, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from shop import settings
from store.decoding import parse_id_token
from store.models import UserProfile, UserRefreshToken, Product, UserProductRelation
from store.permissions import IsAuth
from store.serializers import ProductSerializer, UserProductRelationSerializer
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response

from store.services import LargeResultsSetPagination, ProductFilter


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all().annotate(
        rating=Avg('userproductrelation__rate'), )

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = LargeResultsSetPagination

    search_fields = ['name', 'author']
    ordering_fields = ['price', 'author', ]


class UserBooksRelationView(UpdateModelMixin, GenericViewSet):
    queryset = UserProductRelation.objects.all()
    serializer_class = UserProductRelationSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserProductRelation.objects.get_or_create(user=self.request.user,
                                                                 product_id=self.kwargs['book'], )
        return obj


class GoogleView(APIView):

    def post(self, request):
        token = {'id_token': request.data.get('id_token')}

        try:
            idinfo = id_token.verify_oauth2_token(token['id_token'],
                                                  requests.Request(),
                                                  '29897898232-727dsvebqsfa7kqrddl0hhbbfalg0vjp'
                                                  '.apps.googleusercontent.com')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            payloadAccess = {
                'email': parse_id_token(token['id_token'])['email'],
                'exp': time.time() + 1500
            }
            payloadRefresh = {
                'email': parse_id_token(token['id_token'])['email'],
                'exp': time.time() + 4000
            }
            try:
                User.objects.get(email=parse_id_token(token['id_token'])['email'])
                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)
                access = str(access)[2:-1]
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY)
                refresh = str(refresh)[2:-1]

                response = Response()
                response.set_cookie(key='refresh', value=refresh, httponly=True)
                response.data = {
                    'access': access,
                    'email': parse_id_token(token['id_token'])['email'],
                    'name': parse_id_token(token['id_token'])['name'],
                    'picture': parse_id_token(token['id_token'])['picture'],
                }

                try:
                    UserRefreshToken.objects.get(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name']))

                    UserRefreshToken.objects.filter(user=User.objects.get
                    (username=parse_id_token(token['id_token'])['name'])).update(refresh=refresh)

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
                                         parse_id_token(token['id_token'])['email'])

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)
                access = str(access)[2:-1]
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY)
                refresh = str(refresh)[2:-1]

                UserRefreshToken.objects.create(user=User.objects.get
                (username=parse_id_token(token['id_token'])['name']), refresh=refresh)

                UserProfile.objects.create(user=User.objects.get
                (username=parse_id_token(token['id_token'])['name']),
                                           picture=parse_id_token(token['id_token'])['picture'])

                response = Response()
                response.set_cookie(key='refresh', value=refresh, httponly=True)
                response.data = {
                    'access': access,
                    'email': parse_id_token(token['id_token'])['email'],
                    'name': parse_id_token(token['id_token'])['name'],
                    'picture': parse_id_token(token['id_token'])['picture'],
                }

                return response

        except ValueError as err:
            print(err)
            content = {'message': 'Invalid token'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):

    def post(self, request):
        try:
            data = {'token': request.COOKIES['refresh']}
        except:
            return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)

        payloadAccess = {
            'email': parse_id_token(data['token'])['email'],
            'exp': time.time() + 1500
        }
        payloadRefresh = {
            'email': parse_id_token(data['token'])['email'],
            'exp': time.time() + 4000
        }

        try:
            jwt.decode(data['token'], settings.REFRESH_SECRET_KEY)
        except:
            return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            UserRefreshToken.objects.get(
                user=User.objects.get(email=parse_id_token(request.COOKIES['refresh'])['email']))

            if UserRefreshToken.objects.get(
                    user=User.objects.get(email=parse_id_token(request.COOKIES['refresh'])['email'])).refresh == \
                    request.COOKIES['refresh']:

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)
                access = str(access)[2:-1]
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY)
                refresh = str(refresh)[2:-1]

                UserRefreshToken.objects.filter(
                    user=User.objects.get(email=parse_id_token(data['token'])['email'])).update(refresh=refresh)

                response = Response()

                response.set_cookie(key='refresh', value=refresh, httponly=True)

                response.data = {
                    'access': access,
                    'email': User.objects.get(email=parse_id_token(data['token'])['email']).email,
                    'name': User.objects.get(email=parse_id_token(data['token'])['email']).username,
                    'picture': UserProfile.objects.get(
                        user=User.objects.get(email=parse_id_token(data['token'])['email'])).picture,
                }

                return response
            else:
                return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        try:
            data = parse_id_token(request.COOKIES['refresh'])['email']
            UserRefreshToken.objects.get(user=User.objects.get(email=data)).delete()
        except:
            return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'message': 'Logout success'})
