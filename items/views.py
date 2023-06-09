from django.http import JsonResponse
from django.shortcuts import render

import json

from .models import Item
from .helpers import items_page

# Create your views here.
def search(request, page):
    return render(request, "items/search.html", {
        "page": items_page(request, page),
        "genders": Item.GENDERS,
        "categories": Item.CATEGORIES
    })

def product(request, item_id):
    return render(request, "items/product.html", {
        "item": Item.objects.get(id=item_id)
    })




def updateItem(request):
    data = json.loads(request.body)
    # productId = data['productId']
    # action = data["action"]
    # print("product id:", productId, "action:", action)
    print(data)

    return JsonResponse("Item was added", safe=False)