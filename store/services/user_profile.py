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
    current_user = User.objects.get(email=access['email'])
    name = request.data['name']
    email = request.data['email']
    phone = request.data['phone']
    postal_code = request.data['postalCode']
    try:
        OrderData.objects.get(user=current_user)
        OrderData.objects.filter(user=current_user) \
            .update(name=name, email=email,
                    phone=phone, postalCode=postal_code)
    except OrderData.DoesNotExist:
        OrderData.objects.create(user=current_user, name=name,
                                 email=email, phone=phone,
                                 postalCode=postal_code)
    try:
        UserProfile.objects.get(user=current_user)
        UserProfile.objects.filter(user=current_user). \
            update(orderData=OrderData.objects
                   .get(user=current_user))
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=current_user,
                                   orderData=OrderData.
                                   objects.get(user=current_user))
    return Response({'message': 'success'}, status.HTTP_200_OK)
