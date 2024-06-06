from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cart.models import CartItem, OrderItem, Order, Cart
from .serializers import CartItemSerializer, OrderItemSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_items(request):
    if request.method == 'GET':
        cart_items = CartItem.objects.filter(cart__user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart, created = Cart.objects.get_or_create(user=request.user)
            product_id = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def cart_item_detail(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'PUT':
        serializer = CartItemSerializer(cart_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def order_items(request):
    if request.method == 'GET':
        orders = OrderItem.objects.filter(order__user=request.user)
        serializer = OrderItemSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            order, created = Order.objects.get_or_create(user=request.user)
            product_id = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def order_item_detail(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    if request.method == 'PUT':
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)