from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import UserAddress
from .tokens import account_activation_token



def get_user_address(request):
    try:
        address = UserAddress.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        address = None
    return address


def user_login(request):
    user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
    if user:
        login(request, user)
        messages.success(request, "you're logged in")
        return True
    messages.error(request, "invalid login credentials")
    return False


def user_logout(request):
    logout(request)
    messages.success(request, "you're logged out")
    return


# DODAĆ CHECKI
def user_register(request):
    user = User.objects.create_user(request.POST["username"], request.POST["username"], request.POST["password"])
    user.is_active=False
    user.save()
    activateEmail(request, user, user.email)
    return True


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
        login(request, user)
        messages.success(request, "your account was activated adn you're logged in")
    else:
        messages.error(request, "activation link is invalid")


# DODAĆ IMIĘ UŻYTKOWNIKA
def activateEmail(request, user, to_email):
    mail_subject = "Account activation email"
    message = render_to_string("user/mail_activation.html", {
        "user": "user" ,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, "activation email was sent to your mailbox")
    else:
        messages.error(request, "couldn't send activation email")


# DODAĆ CHECK PW
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
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": PasswordResetTokenGenerator().make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, "password renewal link was sent to your mailbox")
        return True
    else:
        messages.error(request, "couldn't send password renewal email")


# DODAĆ CHECK PW
def change_password(request):
    password = request.POST["password"]
    user = User.objects.get(id=request.user.id)
    user.set_password(password)
    user.save()
    update_session_auth_hash(request, user)
    messages.success(request, "password updated")


# DODAĆ CHECKI INFORMACJI
def change_info(request):
    user = User.objects.get(id=request.user.id)
    user.username = request.POST["email"]
    user.email = request.POST["email"]
    user.first_name = request.POST["first_name"]
    user.last_name = request.POST["last_name"]
    user.save()
    user_address = UserAddress.objects.get(user_id=request.user.id)
    user_address.country = request.POST["country"]
    user_address.city = request.POST["city"]
    user_address.postal = request.POST["postal"]
    user_address.street = request.POST["street"]
    user_address.number = request.POST["number"]
    user_address.save()
    messages.success("information updated")


def delete_account(request):
    if check_password(request.POST["password"], request.user.password):
        user = User.objects.get(id=request.user.id).delete()
        logout(request)
        messages.success(request, "your account was successfully deleted")
        return True
    else:
        messages.error(request, "invalid password")
        return False