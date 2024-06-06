from django.db import models
from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='goods/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goods')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='goods')
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
