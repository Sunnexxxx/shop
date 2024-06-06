from django.urls import path
from cart.api import views

urlpatterns = [
    path('cart/', views.cart_items),
    path('cart/items/<int:item_id>/', views.cart_item_detail),
    path('order/items/', views.order_items),
    path('order/items/<int:item_id>/', views.order_item_detail),
]
