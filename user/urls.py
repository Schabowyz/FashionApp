from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("request_renew", views.request_renew_password, name="request_renew"),
    path("renew/<uidb64>/<token>", views.renew_password, name="renew"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("", views.profile, name="profile"),
    path("password", views.user_change_password, name="password"),
    path("info", views.user_change_info, name="info"),
    path("email", views.user_change_email, name="email"),
    path("address", views.user_change_address, name="address"),
    path("delete", views.user_delete_account, name="delete"),
    path("cart", views.cart, name="cart"),
    path("order", views.order, name="order"),
    path("create_order", views.create_order, name="create_order")
]