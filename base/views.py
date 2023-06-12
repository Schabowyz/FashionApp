from django.shortcuts import render
from user.models import Cart

# Create your views here.
def index(request):
    return render(request, "base/index.html", {
        "cart": Cart.get_cart_items(request)
    })

def about(request):
    return render(request, "base/about.html", {
        "cart": Cart.get_cart_items(request)
    })