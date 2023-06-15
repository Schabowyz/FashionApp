from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .helpers import user_login, user_logout, user_register, get_user_address, get_user_orders, user_activate, renewEmail, user_renew_password, change_password, change_info, change_email, change_address, delete_account, get_cart_info,save_form_data, buy_user, buy_guest
from .models import Cart


########## VIEWS ############

def login_view(request):
    if request.method == "POST":
        if user_login(request):
            response = HttpResponseRedirect(reverse("base:index"))
            response.delete_cookie("cart")
            return response
    return render(request, "user/login.html", {"cart": Cart.get_cart_items(request)})

def register(request):
    if request.method == "POST":
        if user_register(request):
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "user/register.html", {
        "cart": Cart.get_cart_items(request)
    })

def request_renew_password(request):
    if request.method == "POST":
        if renewEmail(request):
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "user/request_renew_password.html", {
        "cart": Cart.get_cart_items(request)
    })

def renew_password(request, uidb64, token):
    if request.method == "POST":
        if user_renew_password(request, uidb64, token):
            return HttpResponseRedirect(reverse("user:login"))
    return render(request, "user/renew_password.html", {
        "uidb64": uidb64,
        "token": token,
        "cart": Cart.get_cart_items(request)
    })

@login_required
def profile(request):
    return render(request, "user/profile.html", {
        "user_address": get_user_address(request),
        "orders": get_user_orders(request),
        "cart": Cart.get_cart_items(request)
    })

def cart(request):
    if request.method == "POST":
        save_form_data(request)
        return HttpResponseRedirect(reverse("user:order"))
    return render(request, "user/cart.html", get_cart_info(request))

def order(request):
    context = get_cart_info(request)
    if not request.session["user_info"] or not context["cart"][0]:
        messages.error(request, "your order is incomplete")
        return HttpResponseRedirect(reverse("user:cart"))
    return render(request, "user/order.html", context)



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
def user_change_email(request):
    change_email(request)
    return HttpResponseRedirect(reverse("user:profile"))

@login_required
def user_change_address(request):
    change_address(request)
    return HttpResponseRedirect(reverse("user:profile"))

@login_required
def user_delete_account(request):
    if delete_account(request):
        return HttpResponseRedirect(reverse("base:index"))
    return HttpResponseRedirect(reverse("user:profile"))

def create_order(request):
    if request.user.is_authenticated:
        buy_user(request)
        return JsonResponse("Order was created", safe=False)
    else:
        buy_guest(request)
        response = JsonResponse("Order was created", safe=False)
        response.delete_cookie("cart")
        return response