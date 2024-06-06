from django.conf import settings
from django.db import models
from products.models import Product
from users.models import CustomUser


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} ({self.quantity})'

    def get_total_price(self):
        return self.product.price * self.quantity


class CartCollection(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart Collection for {self.user.username}'


class CollectedProduct(models.Model):
    collection = models.ForeignKey(CartCollection, on_delete=models.CASCADE, related_name='collected_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

    def get_total_price(self):
        return self.quantity * self.product.price

# models.py


class Order(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (SHIPPED, 'Shipped'),
        (COMPLETED, 'Completed'),
        (DELIVERED, 'Delivered'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    courier = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='assigned_orders')

    def __str__(self):
        return f'Order {self.id}'

    def get_total(self):
        total = sum(item.get_total_price() for item in self.items.all())
        return total



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    shipped = models.BooleanField(default=False)

    def __str__(self):
        return f'OrderItem {self.id}'

    def get_total_price(self):
        return self.product.price * self.quantity

