import time
from django.contrib.auth.models import User
import jwt
from django.db.models import Avg, F, Case, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from shop import settings
from store.models import *
from store.permissions import *
from store.serializers import *
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response

from store.services import *


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().annotate(
        rating=Avg('userproductrelation__rate'),)

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = LargeResultsSetPagination
    search_fields = ['name', 'author']
    ordering_fields = ['price', 'author', ]

    # permission_classes = [FixInCart]

    def retrieve(self, request, *args, **kwargs):
        try:
            access = request.headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            current_user = User.objects.get(email=access['email'])
            instance = self.get_object()
            instance.my_rate = UserProductRelation.objects.get(user=current_user, product_id=instance.id).rate
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            instance = self.get_object()
            instance.my_rate = None
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


class UserProductRateView(UpdateModelMixin, GenericViewSet):
    queryset = UserProductRelation.objects.all()
    serializer_class = ProductRelationSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)

        CartProduct.objects.get_or_create(user=User.objects.get(email=access['email']),
                                          product=Product.objects.get(id=self.kwargs['book']))

        obj, created = UserProductRelation.objects.get_or_create(user=User.objects.get(email=access['email']),
                                                                 product_id=self.kwargs['book'])

        # UserProductRelation.objects.filter(user=User.objects.get(email=access['email']), product_id=self.kwargs['book'],
        #                                    info=CartProduct.objects.get(
        #                                        user=User.objects.get(email=access['email']),
        #                                        product_id=self.kwargs['book'])).update(is_rated=True)
        obj.is_rated = True
        # obj.rating = set_rating(Product.objects.get(id=self.kwargs['book']))
        obj.save()
        return obj


class UserProductCartView(UpdateModelMixin, GenericViewSet, ):
    queryset = CartProduct.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        CartProduct.objects.get_or_create(user=User.objects.get(email=access['email']),
                                          product=Product.objects.get(id=self.kwargs['book']))

        CartProduct.objects.filter(user=User.objects.get(email=access['email']),
                                   product=Product.objects.get(id=self.kwargs['book'])).update(
            copy_count=F('copy_count') + 1)

        Cart.objects.get_or_create(owner=User.objects.get(email=access['email']))

        Cart.objects.filter(owner=User.objects.get(email=access['email'])).first().products.add(
            CartProduct.objects.filter(user=User.objects.get(email=access['email'])).last()
        )
        # Cart.objects.filter(owner=User.objects.get(email=access['email'])). \
        #     update(total_price=F('total_price') + Product.objects.get(id=self.kwargs['book']).price)

        # obj, created = UserProductRelation.objects.get_or_create(user=User.objects.get(email=access['email']),
        #                                                          product_id=self.kwargs['book'],
        #                                                          info=CartProduct.objects.get(
        #                                                              user=User.objects.get(email=access['email']),
        #                                                              product_id=self.kwargs['book']))

        # UserProductRelation.objects.filter(user=User.objects.get(email=access['email']),
        #                                    product_id=self.kwargs['book']).update(in_cart=True)

        # Product.objects.filter(user=User.objects.get(email=access['email']), id=self.kwargs['book']).update(
        #     in_cart=True)
        obj, created = CartProduct.objects.get_or_create(user=User.objects.get(email=access['email']),
                                                         product=Product.objects.get(id=self.kwargs['book']))
        return obj


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [IsAuth]
    serializer_class = CartSerializer

    def get_queryset(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        queryset = self.queryset.filter(owner_id=User.objects.get(email=access['email']).id)

        return queryset


# class CartViewSet(APIView):
#     permission_classes = [IsAuth]
#
#     def get(self, request, format=None):
#         access = self.request.headers['Authorization'].split(' ')[1]
#         access = parse_id_token(access)
#
#         queryset = list(Cart.objects.filter(owner=User.objects.get(email=access['email'])))
#         return Response(queryset)


class CartDeleteView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        if len(list(CartProduct.objects.filter(user=User.objects.get(email=access['email'])))) > 0:

            CartProduct.objects.filter(user=User.objects.get(email=access['email'])).delete()
            Cart.objects.filter(owner=User.objects.get(email=access['email'])).delete()
            # Product.objects.filter(user=User.objects.get(email=access['email'])).update(in_cart=False)

            return Response({"message": "Cart deleted success"}, status.HTTP_200_OK)
        else:
            return Response({"message": "Cart is empty"}, status.HTTP_204_NO_CONTENT)


class CartObjView(UpdateModelMixin, GenericViewSet, ):
    queryset = UserProductRelation.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)

        if CartProduct.objects.filter(user=User.objects.get(email=access['email']),
                                      product=Product.objects.get(id=self.kwargs['book'])).first().copy_count == 1:

            obj = CartProduct.objects.get(user=User.objects.get(email=access['email']), product_id=self.kwargs['book'])
            return obj
        else:
            CartProduct.objects.filter(user=User.objects.get(email=access['email']),
                                       product=Product.objects.get(id=self.kwargs['book'])).update(
                copy_count=F('copy_count') - 1)
            #
            # Cart.objects.filter(owner=User.objects.get(email=access['email'])). \
            #     update(total_price=F('total_price') - Product.objects.get(id=self.kwargs['book']).price)

            # return Response({'message': 'successful deletion of a one book'}, status.HTTP_200_OK)

            obj = CartProduct.objects.get(user=User.objects.get(email=access['email']), product_id=self.kwargs['book'])

            return obj


class CartDelObjView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        try:
            CartProduct.objects.get(user=User.objects.get(email=access['email']), product=Product.objects.get(id=pk))

            CartProduct.objects.filter(user=User.objects.get(email=access['email']),
                                       product=Product.objects.get(id=pk)).delete()
            # Cart.objects.filter(owner=User.objects.get(email=access['email']))
            #
            inst = CartSerializer()
            cart = Cart.objects.filter(owner=User.objects.get(email=access['email'])).first()
            # inst2 = CartProductsSerializer()
            # cartProduct2 = CartProduct.objects.get(user=User.objects.get(email=access['email']),
            #                                        product_id=pk)
            # copy_price = CartProductsSerializer.get_copy_price(inst2, cartProduct2)

            if CartSerializer.get_unique_count(inst, cart) == 0:
                Cart.objects.filter(owner=User.objects.get(email=access['email'])).delete()
            # else:
            #     Cart.objects.filter(owner=User.objects.get(email=access['email'])). \
            #         update(total_price=F('total_price') - copy_price)

            # UserProductRelation.objects.filter(user=User.objects.get(email=access['email']),
            #                                    product=Product.objects.get(id=pk)).update(in_cart=False)

            # Product.objects.filter(user=User.objects.get(email=access['email']), id=pk).update(in_cart=False)

            return Response({'message': 'book successfully deleted'}, status.HTTP_200_OK)
        except:
            return Response({'message': 'book doesnt exists'}, status.HTTP_204_NO_CONTENT)


class FeedbackFormView(UpdateModelMixin, GenericViewSet, ):
    queryset = Feedback.objects.all()
    permission_classes = [IsAuth, ]
    serializer_class = FeedbackSerializer
    lookup_field = 'book'

    def get_object(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)

        obj, created = Feedback.objects.get_or_create(user=User.objects.get(email=access['email']),
                                                      username=User.objects.get(email=access['email']).username, )

        Product.objects.get(id=self.kwargs['book']).comments.add(
            Feedback.objects.get(user=User.objects.get(email=access['email'])))

        return obj


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class GoogleView(APIView):

    def post(self, request):
        token = {'id_token': request.data.get('id_token')}

        try:
            idinfo = id_token.verify_oauth2_token(token['id_token'],
                                                  requests.Request(), '29897898232-727dsvebqsfa7kqrddl0hhbbfalg0vjp.'
                                                                      'apps.googleusercontent.com')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            payloadAccess = {
                'email': parse_id_token(token['id_token'])['email'],
                'exp': time.time() + 15000
            }
            payloadRefresh = {
                'email': parse_id_token(token['id_token'])['email'],
                'exp': time.time() + 40000
            }
            try:
                User.objects.get(email=parse_id_token(token['id_token'])['email'])
                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY, algorithm='HS256')
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY, algorithm='HS256')
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

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY, algorithm='HS256')

                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY, algorithm='HS256')
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
            'exp': time.time() + 15000
        }
        payloadRefresh = {
            'email': parse_id_token(data['token'])['email'],
            'exp': time.time() + 40000
        }

        try:
            jwt.decode(data['token'], settings.REFRESH_SECRET_KEY, algorithms='HS256')
        except:
            return Response({'message': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            UserRefreshToken.objects.get(
                user=User.objects.get(email=parse_id_token(request.COOKIES['refresh'])['email']))

            if UserRefreshToken.objects.get(
                    user=User.objects.get(email=parse_id_token(request.COOKIES['refresh'])['email'])).refresh == \
                    request.COOKIES['refresh']:

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)

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
