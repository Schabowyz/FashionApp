from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def login_view(request):
    return render(request, "user/login.html")

def register(request):
    return render(request, "user/register.html")

def profile(request):
    return render(request, "user/profile.html")

def orders(request):
    return render(request, "user/orders.html")