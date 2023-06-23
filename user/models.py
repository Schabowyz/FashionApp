from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

import json

from items.models import Item


# Create your models here.


class UserAddress(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=56)
    city = models.CharField(max_length=128)
    postal = models.CharField(max_length=16)
    street = models.CharField(max_length=128)
    number = models.CharField(max_length=16)


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    stripe_id = models.CharField(max_length=500, null=True)
    email = models.CharField(max_length=128)
    date = models.DateTimeField()
    status = models.CharField(max_length=32, default=settings.ORDER_STATUSES[0])
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    country = models.CharField(max_length=56)
    city = models.CharField(max_length=128)
    postal = models.CharField(max_length=16)
    street = models.CharField(max_length=128)
    number = models.CharField(max_length=16)

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
    
    def order_overall_price_not_authenticated(request):
        price = 0.0
        items = Cart.get_cart_items(request)[0]
        for item in items:
            price += (item["item_id"].current_price * item["quantity"])
        return round(price, 2)
    

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email
        return user
