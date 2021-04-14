import time
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from store.permissions import *
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response
import random
from store.services import *
from django.forms.models import model_to_dict


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all() \
        .annotate(rating=Avg('userproductrelation__rate'), )

    serializer_class = ProductSerializerAll
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = LargeResultsSetPagination
    search_fields = ['name', 'author']
    ordering_fields = ['price', 'author', ]

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ProductSerializerRetrieve

        try:
            access = request.headers['Authorization'].split(' ')[1]
            access = parse_id_token(access)
            current_user = User.objects.get(email=access['email'])
            instance = self.get_object()
            instance.my_rate = UserProductRelation.objects.get(
                user=current_user,
                product_id=instance.id).rate
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            instance = self.get_object()
            instance.my_rate = None
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


class DiscountProductViewSet(ModelViewSet):
    queryset = Product.objects \
        .filter(sale__gt=0) \
        .annotate(rating=Avg('userproductrelation__rate'), )

    serializer_class = ProductSerializerAll

    idList = [i.id for i in list(queryset)]

    if queryset.count() > 30:
        while queryset.count() != 30:
            rand = random.choice(idList)
            idList.remove(rand)
            queryset.exclude(id=rand)


class UserProductRateView(UpdateModelMixin, GenericViewSet):
    queryset = UserProductRelation.objects.all()
    serializer_class = ProductRelationSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
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


class UserProductCartView(UpdateModelMixin, GenericViewSet, ):
    queryset = CartProduct.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
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


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [IsAuth]
    serializer_class = CartSerializer

    def get_queryset(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        queryset = self.queryset.filter(owner_id=User.objects.get(email=access['email']).id)

        return queryset


class CartDeleteView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
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


class CartObjView(UpdateModelMixin, GenericViewSet, ):
    queryset = UserProductRelation.objects.all()
    serializer_class = CartProductsSerializer
    permission_classes = [IsAuth, ]
    lookup_field = 'book'

    def get_object(self):
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


class CartDelObjView(APIView):
    permission_classes = [IsAuth]

    def delete(self, request, pk):
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
        except:
            return Response({'message': 'book doesnt exists'},
                            status.HTTP_204_NO_CONTENT)


class FeedbackFormView(APIView):
    permission_classes = [IsAuth]

    def post(self, request, pk):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        currentUser = User.objects.get(email=access['email'])

        Feedback.objects.create(
            user=currentUser,
            username=User.objects.get(email=access['email']).username,
            comment=request.data['comment']
        )
        currentFeedback = Feedback.objects.filter(user=currentUser).last()
        Product.objects.get(id=pk).comments.add(currentFeedback)

        responce = Response()
        responce.data = {
            'id': currentFeedback.id,
            'comment': currentFeedback.comment,
            'username': currentFeedback.username,
            'date': currentFeedback.date
        }
        return responce


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class FeedbackRateCommentView(APIView):
    permission_classes = [IsAuth]

    def patch(self, request, pk):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        current_user = User.objects.get(email=access['email'])
        FeedbackRelation.objects.get_or_create(user=current_user, comment_id=pk)
        responce = Response()

        if request.data['data'] == 'like':

            if FeedbackRelation.objects.get(user=current_user, comment_id=pk).like:
                return set_like(current_user, pk, True)
            else:
                return set_like(current_user, pk, False)

        elif request.data['data'] == 'dislike':

            if FeedbackRelation.objects.get(
                    user=current_user,
                    comment_id=pk).dislike:
                FeedbackRelation.objects.filter(
                    user=current_user,
                    comment_id=pk).update(
                    dislike=False
                )
                likeCount = FeedbackRelation.objects.filter(
                    comment_id=pk, like=True).count()
                dislikeCount = FeedbackRelation.objects.filter(
                    comment_id=pk, dislike=True).count()

                responce.data = {
                    'isDisliked': False,
                    'likeCount': likeCount,
                    'dislikeCount': dislikeCount,
                }
                return responce
            else:
                FeedbackRelation.objects.filter(
                    user=current_user,
                    comment_id=pk).update(dislike=True)
                FeedbackRelation.objects.filter(
                    user=current_user,
                    comment_id=pk).update(like=False)

                likeCount = FeedbackRelation.objects.filter(
                    comment_id=pk, like=True).count()
                dislikeCount = FeedbackRelation.objects.filter(
                    comment_id=pk, dislike=True).count()

                responce.data = {
                    'isLiked': False,
                    'isDisliked': True,
                    'likeCount': likeCount,
                    'dislikeCount': dislikeCount,
                }
                return responce
        else:
            return Response({'message': 'invalid request body'},
                            status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuth]

    def get_queryset(self):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        queryset = self.queryset.filter(user=User.objects.get(
            email=access['email']))
        return queryset


class UserProfileFormView(APIView):
    permission_classes = [IsAuth]

    def put(self, request):
        # fields = ['name', 'email', 'phone', 'postalCode']
        # dataFields = []
        #
        # for key, value in request.data.items():
        #     dataFields.append(key)

        # if dataFields.remove('orderItems') == fields:
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        currentUser = User.objects.get(email=access['email'])
        name = request.data['name']
        email = request.data['email']
        phone = request.data['phone']
        postalCode = request.data['postalCode']
        try:
            OrderData.objects.get(user=currentUser)
            OrderData.objects.filter(user=currentUser) \
                .update(name=name, email=email,
                        phone=phone, postalCode=postalCode)
        except:
            OrderData.objects.create(user=currentUser, name=name,
                                     email=email, phone=phone,
                                     postalCode=postalCode)
        try:
            UserProfile.objects.get(user=currentUser)
            UserProfile.objects.filter(user=currentUser). \
                update(orderData=OrderData.objects.get(user=currentUser))
        except:
            UserProfile.objects.create(user=currentUser, orderData=OrderData.objects.get(user=currentUser))

        return Response({'message': 'success'}, status.HTTP_200_OK)
        # return Response({'message': 'validation error'}, status.HTTP_400_BAD_REQUEST)


class MakeOrderView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        access = self.request.headers['Authorization'].split(' ')[1]
        access = parse_id_token(access)
        currentUser = User.objects.get(email=access['email'])
        totalPrice = 0
        totalDiscountPrice = 0
        totalCount = 0
        idData = request.data['id']

        if request.data['confirm'] == 'true':
            idData = [i.product_id for i in
                      CartProduct.objects.filter(user=currentUser)
                      if i.product_id not in idData]

            totalCount = 0
            totalPrice = 0

            for i in request.data['id']:
                cpObj = CartProduct.objects.get(user=currentUser,
                                                product_id=i)
                copyCount = cpObj.copy_count

                if cpObj.copyDiscountPrice is None:
                    copyPrice = cpObj.copyPrice
                else:
                    copyPrice = cpObj.copyDiscountPrice
                CopyProduct.objects.create(user=currentUser, product_id=i,
                                           copyCount=copyCount,
                                           copyPrice=copyPrice)

                totalCount += cpObj.copy_count
                if cpObj.copyDiscountPrice is None:
                    totalPrice += cpObj.copyPrice
                else:
                    totalPrice += cpObj.copyDiscountPrice
            opObj = OrderProduct.objects.create(user=currentUser,
                                                totalCount=totalCount,
                                                totalPrice=totalPrice,
                                                status=1)
            opObj_id = opObj.id
            opObj.save()
            for i in request.data['id']:
                OrderProduct.objects.get(user=currentUser,
                                         id=opObj_id).products.add(
                    CopyProduct.objects.filter(
                        user=currentUser, product_id=i
                    ).last()
                )
            UserProfile.objects.get(user=currentUser). \
                orderItems.add(
                OrderProduct.objects.get(
                    user=currentUser,
                    id=opObj_id)
            )
            for i in request.data['id']:
                CartProduct.objects.filter(
                    user=currentUser, product_id=i).delete()
        try:
            orderData = OrderProduct.objects.get(user=currentUser)
            orderData = {
                'name': orderData.name,
                'email': orderData.email,
                'phone': orderData.phone,
                'postalCode': orderData.postalCode
            }
            # orderData = model_to_dict(orderData)
            # orderData.pop('id')
            # orderData.pop('user')
        except:
            orderData = None

        for i in CartProduct.objects.filter(user=currentUser):
            if i.product_id in idData:
                totalPrice += i.copyPrice
                totalCount += i.copy_count
                if i.copyDiscountPrice is None:
                    totalDiscountPrice = None
                    continue
                totalDiscountPrice += i.copyDiscountPrice

        responce = Response()
        responce.data = {
            'totalCount': totalCount,
            'totalPrice': totalPrice,
            'totalDiscountPrice': totalDiscountPrice,
            'orderData': orderData,
        }
        if request.data['confirm'] == 'true':
            responce.data.pop('orderData')

        return responce


class GoogleView(APIView):

    def post(self, request):
        token = {'id_token': request.data.get('id_token')}

        try:
            idinfo = id_token.verify_oauth2_token(
                token['id_token'], requests.Request(),
                '29897898232-727dsvebqsfa7kqrddl0hhbbfalg0vjp.apps.googleusercontent.com'
            )
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

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY,
                                    algorithm='HS256')
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY,
                                     algorithm='HS256')
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
                    UserRefreshToken.objects.get(
                        user=User.objects.get(
                            email=parse_id_token(token['id_token'])['email'])
                    )
                    UserRefreshToken.objects.filter(
                        user=User.objects.get(
                            email=parse_id_token(
                                token['id_token'])['email'])).update(
                        refresh=refresh
                    )
                except:
                    UserRefreshToken.objects.create(
                        user=User.objects.get(
                            email=parse_id_token(
                                token['id_token'])['email']),
                        refresh=refresh
                    )
                try:
                    UserPhotoProfile.objects.get(
                        user=User.objects.get(
                            email=parse_id_token(
                                token['id_token'])['email'])
                    )
                    UserPhotoProfile.objects.create(
                        user=User.objects.get(
                            email=parse_id_token(
                                token['id_token'])['email']),
                        picture=parse_id_token(token['id_token'])['picture']
                    )
                except:
                    pass
                return response
            except User.DoesNotExist:
                User.objects.create_user(parse_id_token(token['id_token'])['name'],
                                         parse_id_token(token['id_token'])['email'])

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY,
                                    algorithm='HS256')
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY,
                                     algorithm='HS256')
                refresh = str(refresh)[2:-1]

                response = Response()
                response.set_cookie(key='refresh', value=refresh, httponly=True)
                response.data = {
                    'access': access,
                    'email': parse_id_token(token['id_token'])['email'],
                    'name': parse_id_token(token['id_token'])['name'],
                    'picture': parse_id_token(token['id_token'])['picture'],
                }

                UserRefreshToken.objects.create(
                    user=User.objects.get(
                        username=parse_id_token(token['id_token'])['name']),
                    refresh=refresh
                )
                UserPhotoProfile.objects.create(
                    user=User.objects.get(
                        username=parse_id_token(token['id_token'])['name']),
                    picture=parse_id_token(token['id_token'])['picture']
                )
                return response
        except ValueError as err:
            print(err)
            content = {'message': 'Invalid token'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):

    def post(self, request):

        refreshEmail = parse_id_token(request.COOKIES['refresh'])['email']

        try:
            data = {'token': request.COOKIES['refresh']}
        except:
            return Response({'message': 'Auth failed1'},
                            status=status.HTTP_401_UNAUTHORIZED)

        payloadAccess = {
            'email': parse_id_token(data['token'])['email'],
            'exp': time.time() + 15000
        }
        payloadRefresh = {
            'email': parse_id_token(data['token'])['email'],
            'exp': time.time() + 40000
        }

        try:
            jwt.decode(data['token'], settings.REFRESH_SECRET_KEY,
                       algorithms='HS256')
        except:
            return Response({'message': 'Auth failed2'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            UserRefreshToken.objects.get(
                user=User.objects.get(
                    email=refreshEmail)
            )
            if UserRefreshToken.objects.get(
                    user=User.objects.get(
                        email=refreshEmail)).refresh == \
                    request.COOKIES['refresh']:

                access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)
                refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY)
                refresh = str(refresh)[2:-1]

                UserRefreshToken.objects.filter(
                    user=User.objects.get(
                        email=refreshEmail)).update(
                    refresh=refresh
                )
                response = Response()
                response.set_cookie(key='refresh', value=refresh, httponly=True)
                response.data = {
                    'access': access,
                    'email': User.objects.get(email=refreshEmail).email,
                    'name': User.objects.get(email=refreshEmail).username,
                    'picture': UserPhotoProfile.objects.get(
                        user=User.objects.get(email=refreshEmail)).picture,
                }
                return response
            else:
                return Response({'message': 'Auth failed3'},
                                status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'message': 'Auth failed4'},
                            status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        try:
            data = parse_id_token(request.COOKIES['refresh'])['email']
            UserRefreshToken.objects.get(
                user=User.objects.get(
                    email=data)).delete()
        except:
            return Response({'message': 'Auth failed'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Logout success'})
