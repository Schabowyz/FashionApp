from django.urls import path
from . import views

app_name = "items"
urlpatterns = [
    path("", views.search, name="search"),
    path("product_<item_id>", views.product, name="product")
]