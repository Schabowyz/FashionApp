from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

import json

from .models import Item
from user.models import Cart
from .helpers import items_page

# Create your views here.
def search(request, page):
    return render(request, "items/search.html", {
        "page": items_page(request, page),
        "genders": Item.GENDERS,
        "categories": Item.CATEGORIES,
        "cart": Cart.get_cart_items(request)
    })

def product(request, item_id):
    return render(request, "items/product.html", {
        "item": Item.objects.get(id=item_id),
        "cart": Cart.get_cart_items(request)
    })

def updateItem(request):
    data = json.loads(request.body)

    cart = Cart.objects.get_or_create(user_id=User.objects.get(id=request.user.id), item_id=Item.objects.get(id=data['productId']))[0]
    if data["action"] == "add":
        cart.quantity += 1
    elif data["action"] == "remove":
        cart.quantity -= 1
    
    cart.save()

    if cart.quantity <= 0:
        cart.delete()

    return JsonResponse("Item added/removed", safe=False)