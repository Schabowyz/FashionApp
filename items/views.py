from django.shortcuts import render

from .models import Item

# Create your views here.
def search(request):
    return render(request, "items/search.html", {
        "items": Item.objects.all()
    })

def product(request, item_id):
    return render(request, "items/product.html")