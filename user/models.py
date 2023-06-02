from django.contrib.auth.models import User
from django.db import models

from items.models import Item

# Create your models here.
class UserAddress(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=56)
    city = models.CharField(max_length=128)
    postal = models.IntegerField()
    street = models.CharField(max_length=128)
    number = models.CharField(max_length=10)

class Order(models.Model):
    STATUSES = [
        ("pending", "pending"),
        ("payment", "awaiting payment"),
        ("completed", "completed"),
        ("delivery", "in delivery"),
        ("shipped", "shipped")
    ]

    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField()
    status = models.CharField(choices=STATUSES, max_length=16, default=STATUSES[0])
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    country = models.CharField(max_length=56)
    city = models.CharField(max_length=128)
    postal = models.IntegerField()
    street = models.CharField(max_length=128)
    number = models.CharField(max_length=10)

class OrderedItems(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    price_piece = models.FloatField()