from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .helpers import user_login, user_logout, user_register, get_user_address, user_activate


########## VIEWS ############

def login_view(request):
    if request.method == "POST":
        if user_login(request):
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "user/login.html")

def register(request):
    if request.method == "POST":
        if user_register(request):
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "user/register.html")

@login_required
def profile(request):
    return render(request, "user/profile.html", {
        "address": get_user_address(request)
    })

@login_required
def orders(request):
    return render(request, "user/orders.html")


########## FUNCTIONS ############

@login_required
def logout_view(request):
    user_logout(request)
    return HttpResponseRedirect(reverse("base:index"))

def activate(request, uidb64, token):
    user_activate(request, uidb64, token)
    return HttpResponseRedirect(reverse("base:index"))