from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .helpers import user_login, user_logout, user_register, get_user_address, get_user_orders, user_activate, renewEmail, user_renew_password, change_password, change_info, delete_account
from .models import UserAddress


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

def request_renew_password(request):
    if request.method == "POST":
        if renewEmail(request):
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "user/request_renew_password.html")

def renew_password(request, uidb64, token):
    if request.method == "POST":
        if user_renew_password(request, uidb64, token):
            return HttpResponseRedirect(reverse("user:login"))
    return render(request, "user/renew_password.html", {
        "uidb64": uidb64,
        "token": token
    })

@login_required
def profile(request):
    return render(request, "user/profile.html", {
        "user_address": get_user_address(request),
        "orders": get_user_orders(request)
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

@login_required
def user_change_password(request):
    change_password(request)
    return HttpResponseRedirect(reverse("user:profile"))

@login_required
def user_change_info(request):
    change_info(request)
    return HttpResponseRedirect(reverse("user:profile"))

@login_required
def user_delete_account(request):
    if delete_account(request):
        return HttpResponseRedirect(reverse("base:index"))
    return HttpResponseRedirect(reverse("user:profile"))