from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

import datetime
import json

from .models import UserAddress, Order, OrderedItems, Cart
from items.models import Item
from .tokens import account_activation_token



##############################    GETTERS    ##############################


def get_user_address(request):
    try:
        address = UserAddress.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        address = None
    return address


def get_user_orders(request):
    orders_list = []
    orders = Order.objects.filter(user_id=request.user.id)
    for instance in orders:
        order = {}
        order["order_info"] = instance
        order["order_items"] = OrderedItems.objects.select_related("item_id").filter(order_id=instance.id)
        orders_list.append(order)
    return orders_list[::-1]



##############################    CHECKS    ##############################


def check_demo_user(request):
    if request.user.username == "demo@user.com":
        messages.error(request, "you can't change demo user's credentials")
        return True
    return False


def check_username(request):
    error = False
    try:
        validate_email(request.POST["email"])
    except ValidationError:
        messages.error(request, "invalid email address")
        error = True
    try:
        User.objects.get(username=request.POST["email"])
        messages.error(request, "email already taken")
        error = True
    except ObjectDoesNotExist:
        pass
    return error
    

def check_password(request):
    error = False
    if request.POST["password"] != request.POST["repeat_password"]:
        messages.error(request, "passwords don't match")
        error = True
    try:
        validate_password(request.POST["password"])
    except ValidationError:
        messages.error(request, "password doesn't meet the requirements")
        error = True
    return error



##############################    USER ACCOUNT SERVICE    ##############################


def user_login(request):
    user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
    if user:
        cookie_cart = get_cart_info(request)
        login(request, user)
        for item in cookie_cart["cart"][0]:
            cart = Cart.objects.get_or_create(user_id=User.objects.get(id=request.user.id), item_id=item["item_id"])
            if cart[1] == True:
                cart[0].quantity = item["quantity"]
            elif cart[1] == False:
                cart[0].quantity += item["quantity"]
            cart[0].save()
        messages.success(request, "you're logged in now")
        return True
    messages.error(request, "invalid login credentials")
    return False


def user_logout(request):
    logout(request)
    messages.success(request, "you're logged out now")
    return


# DODAĆ CHECKI
def user_register(request):
    error = False
    if check_username(request):
        error = True
    if check_password(request):
        error = True

    if not error:
        user = User.objects.create_user(request.POST["email"], request.POST["email"], request.POST["password"])
        user.is_active=False
        user.save()
        activateEmail(request, user, user.email)
        return True
    else:
        return False


def user_activate(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "account activated, you can log in now")
    else:
        messages.error(request, "activation link is invalid")


# DODAĆ IMIĘ UŻYTKOWNIKA
def activateEmail(request, user, to_email):
    mail_subject = "Account activation email"
    message = render_to_string("user/mail_activation.html", {
        "user": "user" ,
        "domain": settings.DOMAIN,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
        "protocol": "https://" if request.is_secure() else "http://"
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, "activation email was sent to your mailbox, check spam folder")
    else:
        messages.error(request, "couldn't send activation email")


def user_renew_password(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        user.set_password(request.POST["password"])
        user.save()
        messages.success(request, "new password was set, you can login now")
        return True
    else:
        messages.error(request, "something went wrong")


def renewEmail(request):
    to_email = request.POST["email"]
    try:
        user = User.objects.get(email = to_email)
    except User.DoesNotExist:
        messages.error(request, "wrong email address")
        return
    mail_subject = "Password renewal email"
    message = render_to_string("user/mail_renew_password.html", {
        "user": "user",
        "domain": settings.DOMAIN,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": PasswordResetTokenGenerator().make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, "password renewal link was sent to your mailbox, check spam folder")
        return True
    else:
        messages.error(request, "couldn't send password renewal email")


# DODAĆ CHECK PW
def change_password(request):
    if request.POST["password"] != request.POST["repeat_password"]:
        messages.error(request, "passwords don't match")
        return
    user = User.objects.get(id=request.user.id)
    user.set_password(request.POST["password"])
    user.save()
    update_session_auth_hash(request, user)
    messages.success(request, "password updated")


# DODAĆ CHECKI INFORMACJI
def change_info(request):
    user = User.objects.get(id=request.user.id)
    user.first_name = request.POST["first_name"]
    user.last_name = request.POST["last_name"]
    user.save()
    messages.success(request, "information updated")


def change_email(request):
    user = User.objects.get(id=request.user.id)
    user.username = request.POST["email"]
    user.email = request.POST["email"]
    user.save()


def change_address(request):
    address = UserAddress.objects.get(user_id=request.user.id)
    address.country = request.POST["country"]
    address.city = request.POST["city"]
    address.postal = request.POST["postal"]
    address.street = request.POST["street"]
    address.number = request.POST["number"]
    address.save()
    messages.success(request, "information updated")


def delete_account(request):
    if check_password(request.POST["password"], request.user.password):
        user = User.objects.get(id=request.user.id).delete()
        logout(request)
        messages.success(request, "your account was successfully deleted")
        return True
    else:
        messages.error(request, "invalid password")
        return False
    


##############################    CART AND ORDER SERVICE    ##############################


# Gets info about users cart, either from db if user is logged or from session if not
def get_cart_info(request):
    if request.user.is_authenticated:
        cart = Cart.get_cart_items(request)
        price = Cart.order_overall_price(request)
        try:
            user_address = UserAddress.objects.get(user_id=request.user.id)
        except UserAddress.DoesNotExist:
            user_address = None
    else:
        try:
            cart_cookie = json.loads(request.COOKIES["cart"])
        except KeyError:
            cart_cookie = {}
        
        cart = []
        quantity = 0
        price = 0
        for key, value in cart_cookie.items():
            item = {}
            item["item_id"] = Item.objects.get(id=int(key))
            item["quantity"] = value["quantity"]
            item["item_overall_price"] = item["quantity"] * item["item_id"].current_price
            cart.append(item)
            price += item["item_overall_price"]
            quantity += item["quantity"]
        cart = (cart, quantity)
        try:
            user_address = request.session["user_info"]
        except:
            user_address = None

    return {"cart": cart, "price": price, "user_address": user_address}


# Order form user info saving
def save_form_data(request):
    valid_email = True
    if request.user.is_authenticated:
        email = request.user.email
    else:
        email = request.POST["email"]
        try:
            validate_email(email)
        except:
            valid_email = False
            messages.error(request, "invalid email address")
    request.session["user_info"] = {
        "email": email,
        "first_name": request.POST["first_name"],
        "last_name": request.POST["last_name"],
        "street": request.POST["street"],
        "number": request.POST["number"],
        "city": request.POST["city"],
        "postal": request.POST["postal"],
        "country": request.POST["country"]
    }

    for value in request.session["user_info"].values():
        if not value:
            messages.error(request, "please provide missing information")
            return False
    if not valid_email:
        return False

    if request.POST.get("remember") == "true":
        user = User.objects.get(id=request.user.id)
        user.first_name = request.POST["first_name"]
        user.last_name = request.POST["last_name"]
        user.save()
        try:
            user_address = UserAddress.objects.get(user_id=user)
            user_address.country = request.POST["country"]
            user_address.city = request.POST["city"]
            user_address.postal = request.POST["postal"]
            user_address.street = request.POST["street"]
            user_address.number = request.POST["number"]
        except ObjectDoesNotExist:
            user_address = UserAddress.objects.create(
                user_id = user,
                country = request.POST["country"],
                city = request.POST["city"],
                postal = request.POST["postal"],
                street = request.POST["street"],
                number = request.POST["number"],
            )
        user_address.save()
        messages.success(request, "profile information updated")

    return True


def buy_user(request):
    # Creates an entry in orders db
    order = Order(
        user_id = User.objects.get(id=request.user.id),
        email = request.session["user_info"]["email"],
        date = datetime.datetime.now(),
        status = settings.ORDER_STATUSES[0],
        first_name = request.session["user_info"]["first_name"],
        last_name = request.session["user_info"]["last_name"],
        country = request.session["user_info"]["country"],
        city = request.session["user_info"]["city"],
        postal = request.session["user_info"]["postal"],
        street = request.session["user_info"]["street"],
        number = request.session["user_info"]["number"],
    )
    order.save()

    # Add cart items to order
    for item in Cart.get_cart_items(request)[0]:
        listed_item = Item.objects.get(id=item.item_id.id)
        ordered_item = OrderedItems(order_id=order, item_id=item.item_id, quantity=item.quantity, price_piece=listed_item.current_price)
        ordered_item.save()

    # Delete items from cart
    cart = Cart.objects.filter(user_id=request.user.id)
    cart.delete()

    # Deletes user_info from session data
    del request.session["user_info"]

    return order


def buy_guest(request):
    # Creates entry in orders db
    order = Order(
        user_id = None,
        email = request.session["user_info"]["email"],
        date = datetime.datetime.now(),
        status = settings.ORDER_STATUSES[0],
        first_name = request.session["user_info"]["first_name"],
        last_name = request.session["user_info"]["last_name"],
        country = request.session["user_info"]["country"],
        city = request.session["user_info"]["city"],
        postal = request.session["user_info"]["postal"],
        street = request.session["user_info"]["street"],
        number = request.session["user_info"]["number"],
    )
    order.save()

    # Add cart items to order
    for item in Cart.get_cart_items(request)[0]:
        listed_item = item["item_id"]
        ordered_item = OrderedItems(order_id=order, item_id=listed_item, quantity=item["quantity"], price_piece=listed_item.current_price)
        ordered_item.save()

    # Deletes user_info from session data
    del request.session["user_info"]

    return order


def order_email(request, to_email, order, name):
    mail_subject = "Order number " + str(order.id)
    message = render_to_string("user/mail_order.html", {
        "name": name,
        "items": OrderedItems.objects.filter(order_id=order),
        "order": order
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"
    if email.send():
        messages.success(request, "confirmation email sent, check spam folder")
    else:
        messages.error(request, "failed to send confirmation email")