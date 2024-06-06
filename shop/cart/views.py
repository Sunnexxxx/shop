from django.core.mail import send_mail
from django.conf import settings
import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from products.forms import AddToCartForm
from products.models import Product
from users.models import CustomUser
from .models import Cart, CartItem, CartCollection, CollectedProduct, OrderItem, Order


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = sum(item.get_total_price() for item in cart.items.all())
    return render(request, 'cart_detail.html', {'cart': cart, 'total_price': total_price})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


@require_POST
@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    data = json.loads(request.body)
    new_quantity = data.get('quantity')
    if new_quantity is not None and int(new_quantity) > 0:
        cart_item.quantity = int(new_quantity)
        cart_item.save()
        cart = cart_item.cart
        total_price = sum(item.get_total_price() for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'item_total': cart_item.get_total_price(),
            'cart_total': total_price,
        })
    return JsonResponse({'success': False})


@login_required
def collect_cart(request):
    cart_collection = CartCollection.objects.create(user=request.user)
    cart = Cart.objects.get(user=request.user)
    for cart_item in cart.items.all():
        CollectedProduct.objects.create(
            collection=cart_collection,
            product=cart_item.product,
            quantity=cart_item.quantity
        )

    cart.items.all().delete()

    return redirect('cart_detail')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_total_price = order.get_total()
    return render(request, 'order_detail.html', {'order': order, 'order_total_price': order_total_price})



@login_required
def cart_to_order(request):
    cart = get_object_or_404(Cart, user=request.user)

    if cart.items.exists():
        order = Order.objects.create(user=request.user)

        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            product = item.product
            seller = product.seller
            notify_seller(seller, order)

            item.delete()

        messages.success(request, 'Your order has been placed successfully.')
        return redirect('order_detail', order_id=order.id)
    else:
        messages.error(request, 'Your cart is empty. Please add products to your cart first.')
        return redirect('cart_detail')


def notify_seller(seller, order):
    subject = 'New Order Notification'
    message = f'Hello {seller.username},\n\nYou have a new order: {order.id}. Please check your dashboard.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [seller.email]
    send_mail(subject, message, email_from, recipient_list)


@require_POST
@login_required
def update_order_item(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    data = json.loads(request.body)
    new_quantity = data.get('quantity')
    if new_quantity is not None and int(new_quantity) > 0:
        order_item.quantity = int(new_quantity)
        order_item.save()
        order = order_item.order
        total_price = sum(item.get_total_price() for item in order.items.all())
        return JsonResponse({
            'success': True,
            'item_total': order_item.get_total_price(),
            'order_total': total_price,
        })
    return JsonResponse({'success': False})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


@login_required
def seller_order_list(request):
    if request.user.user_type == 'S':
        products_by_seller = Product.objects.filter(seller=request.user)
        order_items_by_seller = OrderItem.objects.filter(product__in=products_by_seller)
        orders = Order.objects.filter(items__in=order_items_by_seller).distinct().order_by('-created_at')

        return render(request, 'seller_order_list.html', {'orders': orders})


@login_required
def seller_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    seller_products = Product.objects.filter(seller=request.user)
    order_items = order.items.filter(product__seller=request.user)
    order_total_price = sum(item.get_total_price() for item in order_items)

    if request.method == 'POST':
        if all(item.is_shipped for item in order.items.filter(product__seller=request.user)):
            order.status = 'in_transit'
            order.save()
            return redirect('seller_order_detail', order_id=order.id)

    return render(request, 'seller_order_detail.html', {
        'order_total_price': order_total_price,
        'order': order,
        'order_items': order_items
    })


@login_required
@require_POST
def confirm_shipment(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    product = order_item.product

    if product.stock >= order_item.quantity:
        product.stock -= order_item.quantity
        product.save()

        order_item.shipped = True
        order_item.save()

        order = order_item.order
        if all(item.shipped for item in order.items.all()):
            order.status = Order.IN_PROGRESS
            order.save()

        return redirect('seller_order_detail', order_id=order_item.order.id)
    else:
        return redirect('seller_order_detail', order_id=order_item.order.id, error='Not enough stock available')


@login_required
def courier_order_list(request):
    if request.user.user_type != CustomUser.COURIER:
        return redirect('home')

    orders = Order.objects.filter(
        (Q(status=Order.IN_PROGRESS) & Q(courier__isnull=True)) |
        (Q(status=Order.DELIVERED) & Q(courier=request.user))
    )
    return render(request, 'courier_order_list.html', {'orders': orders})


@login_required
def courier_order_detail(request, order_id):
    if request.user.user_type != CustomUser.COURIER:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    order_total_price = sum(item.get_total_price() for item in order.items.all())
    buyer = order.user

    if request.method == 'POST':
        if 'accept_order' in request.POST:
            order.status = Order.DELIVERED
            order.courier = request.user
        elif 'mark_completed' in request.POST:
            order.status = Order.COMPLETED
        order.save()
        return redirect('courier_order_list')

    return render(request, 'courier_order_detail.html', {
        'order_total_price': order_total_price,
        'order': order,
        'order_items': order.items.all(),
        'buyer': buyer
    })


@login_required
def confirm_delivery(request, order_id):
    if request.user.user_type != CustomUser.COURIER:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    order.status = Order.DELIVERED
    order.courier = request.user
    order.save()
    return redirect('courier_order_list')


@require_POST
def add_to_cart(request):
    form = AddToCartForm(request.POST)
    if form.is_valid():
        product_id = form.cleaned_data['product_id']
        quantity = form.cleaned_data['quantity']
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return JsonResponse({'success': False, 'error': 'Not enough stock available'}, status=400)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()

        messages.success(request, 'Item added to cart successfully.')
        return JsonResponse({'success': True, 'message': 'Item added to cart successfully.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid form submission.'}, status=400)



class SellerProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'seller_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)