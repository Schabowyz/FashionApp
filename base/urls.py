from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("social/signup/", views.signup_redirect, name="signup_redirect")
]