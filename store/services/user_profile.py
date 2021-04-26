from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def get_user_profile(self, ):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    try:
        queryset = UserProfile.objects.get(
            user=User.objects.get(
                email=access['email'])
        )
    except UserProfile.DoesNotExist:
        return Response({"orderData": None, "orderItems": None},
                        status=status.HTTP_204_NO_CONTENT)
    serializer = UserProfileSerializer(queryset, )
    return Response(serializer.data)


def fill_user_profile_form(self, request):
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
    except OrderData.DoesNotExist:
        OrderData.objects.create(user=currentUser, name=name,
                                 email=email, phone=phone,
                                 postalCode=postalCode)
    try:
        UserProfile.objects.get(user=currentUser)
        UserProfile.objects.filter(user=currentUser). \
            update(orderData=OrderData.objects
                   .get(user=currentUser))
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=currentUser,
                                   orderData=OrderData.
                                   objects.get(user=currentUser))
    return Response({'message': 'success'}, status.HTTP_200_OK)
