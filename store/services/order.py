from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def make_order(self, request):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    currentUser = User.objects.get(email=access['email'])
    totalPrice = 0
    totalDiscountPrice = 0
    totalCount = 0
    idData = request.data['id']

    if request.data['confirm']:
        idData = [i.product_id for i in
                  CartProduct.objects.filter(user=currentUser)
                  if i.product_id not in idData]

        arrJson = []

        if not idData:
            Cart.objects.filter(owner=currentUser).delete()

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

            totalCount += cpObj.copy_count

            if cpObj.copyDiscountPrice is None:
                totalPrice += cpObj.copyPrice
            else:
                totalPrice += cpObj.copyDiscountPrice

            name = Product.objects.get(id=i).name
            author = Product.objects.get(id=i).author
            image = Product.objects.get(id=i).image

            arrJson.append({
                'id': i,
                'name': name,
                'author': author,
                'image': image,
                'copyCount': copyCount,
                'copyPrice': str(copyPrice),
            }
            )
        opObj = OrderProduct.objects.create(user=currentUser,
                                            totalCount=totalCount,
                                            totalPrice=totalPrice,
                                            status='Order processing')
        opObj_id = opObj.id
        opObj.save()

        OrderProduct.objects.filter(user=currentUser, id=opObj_id) \
            .update(products=arrJson)

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
        orderData = OrderData.objects.get(user=currentUser)
        orderData = {
            'name': orderData.name,
            'email': orderData.email,
            'phone': orderData.phone,
            'postalCode': orderData.postalCode
        }
    except OrderData.DoesNotExist:
        orderData = None

    for i in CartProduct.objects.filter(user=currentUser):
        if i.product_id in idData:
            totalPrice += i.copyPrice
            totalCount += i.copy_count
            if i.copyDiscountPrice is None:
                totalDiscountPrice = None
                continue
            totalDiscountPrice += i.copyDiscountPrice

    response = Response()
    response.data = {
        'totalCount': totalCount,
        'totalPrice': totalPrice,
        'totalDiscountPrice': totalDiscountPrice,
        'orderData': orderData,
    }
    if request.data['confirm']:
        return Response({'message': 'order successfully'},
                        status=status.HTTP_200_OK)
    return response
