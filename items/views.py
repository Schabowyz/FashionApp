from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

import json

from .models import Item
from user.models import Cart
from .helpers import items_page, get_genders_dict, get_categories_dict

# Create your views here.
def search(request, page):

    genders = get_genders_dict()
    categories = get_categories_dict()
    gender_filters = ()
    category_filters = ()
    search = ""

    if request.method == "POST":

        genders = get_genders_dict()
        for gender in genders.keys():
            if request.POST.get(gender) == "yes":
                genders[gender] = True
                gender_filters += (gender,)

        categories = get_categories_dict()
        for category in categories.keys():
            if request.POST.get(category) == "yes":
                categories[category] = True
                category_filters += (category,)

        if request.POST.get("query"):
            search = request.POST.get("query")
    
    return render(request, "items/search.html", {
        "query": search,
        "genders": genders,
        "categories": categories,
        "page": items_page(page, gender_filters, category_filters, search),
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