from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver


class CustomUser(AbstractUser):
    USER = 'U'
    SELLER = 'S'
    COURIER = 'C'

    USER_TYPE_CHOICES = [
        (USER, 'Buyer'),
        (SELLER, 'Seller'),
        (COURIER, 'Courier'),
    ]

    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, default=USER)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    groups = models.ManyToManyField('auth.Group', related_name='custom_users')

    def __str__(self):
        return self.username


@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == CustomUser.USER:
            group_name = 'Buyers'
        elif instance.user_type == CustomUser.SELLER:
            group_name = 'Sellers'
        elif instance.user_type == CustomUser.COURIER:
            group_name = 'Couriers'
        else:
            return

        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)


def create_groups(sender, **kwargs):
    if kwargs['using'] == 'default':
        buyers_group, _ = Group.objects.get_or_create(name='Buyers')
        sellers_group, _ = Group.objects.get_or_create(name='Sellers')
        couriers_group, _ = Group.objects.get_or_create(name='Couriers')


post_migrate.connect(create_groups, sender=None)
