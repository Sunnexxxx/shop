from django.urls import path
from .views import *


urlpatterns = [
    path('', MainPage.as_view(), name='main'),
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('owner/', Owner.as_view(), name='owner'),
    path('create/', ProductCreate.as_view(), name='create'),
    path('buyer/', Buyer.as_view(), name='buyer'),
    path('product/<int:pk>', Detail.as_view(), name='product'),
    path('vacancy/<int:pk>/update/', ProductUpdate.as_view(), name='product_update'),
    path('vacancy/<int:pk>/delete/', ProductDelete.as_view(), name='product_delete'),
    path('detail_owner/<int:pk>/', DetailOwner.as_view(), name='detail_o'),

    ]
