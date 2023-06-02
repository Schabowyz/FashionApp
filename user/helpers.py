from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


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

def user_register(request):
    user = User.objects.create_user(request.POST["username"], request.POST["username"], request.POST["password"])
    user.save()
    login(request, user)
    messages.success(request, "you're registered now")
    return True