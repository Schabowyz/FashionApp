from django.shortcuts import render

# Create your views here.
def search(request):
    return render(request, "items/search.html")

def product(request, item_id):
    return render(request, "items/product.html")