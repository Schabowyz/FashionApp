from django.contrib.auth.models import User
from django.db import models

import json

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
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    email = models.CharField(max_length=128)
    date = models.DateTimeField()
    status = models.CharField(choices=STATUSES, max_length=16, default=STATUSES[0])
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    country = models.CharField(max_length=56)
    city = models.CharField(max_length=128)
    postal = models.IntegerField()
    street = models.CharField(max_length=128)
    number = models.CharField(max_length=10)

    def overall_price(self):
        price = 0.00
        items = OrderedItems.objects.values_list("quantity", "price_piece").filter(order_id=self.id)
        for item in items:
            price += item[0] * item[1]
        return price

    
class OrderedItems(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=0)
    price_piece = models.FloatField(default=1)
    
    def overall_price(self):
        return self.quantity * self.price_piece
    

class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def get_cart_items(request):
        if request.user.is_authenticated:
            return (Cart.objects.select_related("item_id").filter(user_id=request.user.id), Cart.get_cart_items_quantity(request))
        else:
            try:
                cart_cookie = json.loads(request.COOKIES["cart"])
            except KeyError:
                cart_cookie = {}

            cart = []
            quantity = 0
            for key, value in cart_cookie.items():
                item = {}
                item["item_id"] = Item.objects.get(id=int(key))
                item["quantity"] = value["quantity"]
                cart.append(item)
                quantity += item["quantity"]
            
            return (cart, quantity)

    
    def get_cart_items_quantity(request):
        quantity = 0
        for item in Cart.objects.filter(user_id=request.user.id):
            quantity += item.quantity
        return quantity
    
    def item_overall_price(self):
        return self.quantity*self.item_id.current_price
    
    def order_overall_price(request):
        items = Cart.objects.filter(user_id=request.user.id)
        price = 0.00
        for item in items:
            price += item.item_overall_price()
        return price