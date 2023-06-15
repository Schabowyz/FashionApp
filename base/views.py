from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
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

def signup_redirect(request):
    messages.error(request, "account using this email address already exists")
    return HttpResponseRedirect(reverse("base:index"))