from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

import stripe

from .helpers import user_login, user_logout, user_register, get_user_address, get_user_orders, user_activate, renewEmail, user_renew_password, change_password, change_info, change_email, change_address, delete_account, get_cart_info,save_form_data, buy_user, buy_guest, order_email, check_demo_user
from .models import Cart, Order



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
        if request.POST["email"] == "demo@user.com":
            messages.error(request, "you can't request password change for demo user")
            return HttpResponseRedirect(reverse("user:request_renew"))
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

    # Gets info for page render - user and cart
    context = get_cart_info(request)
    if not request.session["user_info"] or not context["cart"][0]:
        messages.error(request, "your order is incomplete")
        return HttpResponseRedirect(reverse("user:cart"))
    
    # Stripe session and payment
    if request.method == "POST":

        # Creates database entry for the order
        if request.user.is_authenticated:
            order = buy_user(request)
        else:
            order = buy_guest(request)

        # Gets items from cart to stripe fromat
        line_items = []
        for item in context["cart"][0]:
            if request.user.is_authenticated:
                unit_amount = int(item.item_id.current_price * 100)
                name = item.item_id.name
                quantity = item.quantity
            else:
                unit_amount = int(item["item_id"].current_price * 100)
                name = item["item_id"].name
                quantity = item["quantity"]
            line_items.append({
                "price_data": {
                    "currency": "eur",
                    "unit_amount": unit_amount,
                    "product_data": {
                        "name": name
                    }
                },
                "quantity": quantity
            })
        # Creates stripe session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ["card"],
            line_items = line_items,
            mode = "payment",
            customer_creation = "always",
            success_url = settings.REDIRECT_DOMAIN + "/payment_successful?session_id={CHECKOUT_SESSION_ID}&order_id=" + str(order.id),
            cancel_url = settings.REDIRECT_DOMAIN + "/payment_cancelled",
        )

        order.stripe_id = checkout_session["id"]
        order.stauts = settings.ORDER_STATUSES[1]
        order.save()

        # Redirects to correct url and removes cart cookie
        response = HttpResponseRedirect(checkout_session.url)
        response.delete_cookie("cart")
        return response

    return render(request, "user/order.html", context)


def payment_cancelled(request):
    return render(request, "user/payment_cancelled.html")



########## FUNCTIONS ############


def payment_successful(request):
    order = Order.objects.get(id=request.GET.get("order_id", None))
    order.status = settings.ORDER_STATUSES[2]
    order.save()
    messages.success(request, "transaction successful, order created")

    order_email(request, order.email, order, order.first_name + " " + order.last_name)

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("user:profile"))
    else:
        return HttpResponseRedirect(reverse("user:cart"))


@login_required
def logout_view(request):
    user_logout(request)
    return HttpResponseRedirect(reverse("base:index"))


def activate(request, uidb64, token):
    user_activate(request, uidb64, token)
    return HttpResponseRedirect(reverse("base:index"))  


@login_required
def user_change_password(request):
    if not check_demo_user(request):
        change_password(request)
    return HttpResponseRedirect(reverse("user:profile"))


@login_required
def user_change_info(request):
    if not check_demo_user(request):
        change_info(request)
    return HttpResponseRedirect(reverse("user:profile"))


@login_required
def user_change_email(request):
    if not check_demo_user(request):
        change_email(request)
    return HttpResponseRedirect(reverse("user:profile"))


@login_required
def user_change_address(request):
    if not check_demo_user(request):
        change_address(request)
    return HttpResponseRedirect(reverse("user:profile"))


@login_required
def user_delete_account(request):
    if not check_demo_user(request):
        if delete_account(request):
            return HttpResponseRedirect(reverse("base:index"))
    return HttpResponseRedirect(reverse("user:profile"))