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
    path("order/payment_successful", views.payment_successful, name="payment_successful"),
    path("order/payment_cancelled", views.payment_cancelled, name="payment_cancelled"),
    # path("stripe_webhook", views.stripe_webhook, name="stripe_webhook")
]