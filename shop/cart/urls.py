from django.urls import path
from . import views
from .views import SellerProductListView

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('collect/', views.collect_cart, name='collect_cart'),
    path('order/', views.cart_to_order, name='cart_to_order'),
    path('orders/', views.order_list, name='order_list'),
    path('my-products/', SellerProductListView.as_view(), name='seller_product_list'),
    path('seller/orders/', views.seller_order_list, name='seller_order_list'),
    path('seller/orders/<int:order_id>', views.seller_order_detail, name='seller_order_detail'),
    path('seller/orders/<int:item_id>/confirm-shipment/', views.confirm_shipment, name='confirm_shipment'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/update/<int:order_id>', views.update_order_item, name='update_order_item'),
    path('seller/orders/confirm_shipment/<int:item_id>/', views.confirm_shipment, name='confirm_shipment'),
    path('courier/orders/', views.courier_order_list, name='courier_order_list'),
    path('courier/orders/<int:order_id>/', views.courier_order_detail, name='courier_order_detail'),
    path('courier/orders/confirm_delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
]
