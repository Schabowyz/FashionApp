from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import UserAddress
from .tokens import account_activation_token


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

# DODAĆ CHECK DO FORMA
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

def get_user_address(request):
    try:
        address = UserAddress.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        address = None
    return address

# DODAĆ IMIĘ UŻYTKOWNIKA
def activateEmail(request, user, to_email):
    mail_subject = "Account activation mail"
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