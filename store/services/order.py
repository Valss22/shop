from rest_framework import status
from store.serializers import *
from store.models import *
from rest_framework.response import Response


def make_order(self, request):
    access = self.request.headers['Authorization'].split(' ')[1]
    access = parse_id_token(access)
    current_user = User.objects.get(email=access['email'])
    total_price = 0
    total_discount_price = 0
    total_count = 0
    id_data = request.data['id']

    if request.data['confirm']:
        id_data = [i.product_id for i in
                   CartProduct.objects.filter(user=current_user)
                   if i.product_id not in id_data]

        arr_json = []

        if not id_data:
            Cart.objects.filter(owner=current_user).delete()

        total_count = 0
        total_price = 0

        for i in request.data['id']:
            cp_obj = CartProduct.objects.get(
                user=current_user, product_id=i
            )
            copy_count = cp_obj.copy_count

            if cp_obj.copy_discount_price is None:
                copy_price = cp_obj.copyPrice
            else:
                copy_price = cp_obj.copy_discount_price

            total_count += cp_obj.copy_count

            if cp_obj.copy_discount_price is None:
                total_price += cp_obj.copyPrice
            else:
                total_price += cp_obj.copy_discount_price

            name = Product.objects.get(id=i).name
            author = Product.objects.get(id=i).author
            image = Product.objects.get(id=i).image

            arr_json.append({
                'id': i,
                'name': name,
                'author': author,
                'image': image,
                'copyCount': copy_count,
                'copyPrice': str(copy_price),
            })
        op_obj = OrderProduct.objects.create(
            user=current_user,
            totalCount=total_count,
            totalPrice=total_price,
            status='Order processing'
        )
        op_obj_id = op_obj.id
        op_obj.save()

        OrderProduct.objects.filter(user=current_user, id=op_obj_id) \
            .update(products=arr_json)

        UserProfile.objects.get(user=current_user). \
            orderItems.add(
            OrderProduct.objects.get(
                user=current_user,
                id=op_obj_id)
        )
        for i in request.data['id']:
            CartProduct.objects.filter(
                user=current_user, product_id=i).delete()
    try:
        orderData = OrderData.objects.get(user=current_user)
        orderData = {
            'name': orderData.name,
            'email': orderData.email,
            'phone': orderData.phone,
            'postalCode': orderData.postalCode
        }
    except OrderData.DoesNotExist:
        orderData = None

    for i in CartProduct.objects.filter(user=current_user):
        if i.product_id in id_data:
            total_price += i.copyPrice
            total_count += i.copy_count
            if i.copy_discount_price is None:
                total_discount_price = None
                continue
            total_discount_price += i.copy_discount_price

    response = Response()
    response.data = {
        'totalCount': total_count,
        'totalPrice': total_price,
        'totalDiscountPrice': total_discount_price,
        'orderData': orderData,
    }
    if request.data['confirm']:
        return Response({'message': 'order successfully'},
                        status=status.HTTP_200_OK)
    return response
