from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField('Name', max_length=255)
    price = models.PositiveIntegerField('Price', default=0)
    quantity = models.PositiveIntegerField('Quantity')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, verbose_name="Category", null=True)
    description = models.TextField('Description', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField('Slug', max_length=255, blank=True, unique=True)

    def __str__(self):
        return f"{self.name} {self.price} {self.category}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.slug = slugify(f"{self.name} - {self.price}")
        super().save(force_insert, force_update, using, update_fields)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField('Quantity')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField('Slug', max_length=255, blank=True, unique=True)
    paid = models.BooleanField('Paid', default=False)
    delivered = models.BooleanField('Delivered', default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.product}"




