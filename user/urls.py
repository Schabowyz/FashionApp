from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("", views.profile, name="profile"),
    path("orders", views.orders, name="orders")
]