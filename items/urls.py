from django.urls import path
from . import views

app_name = "items"
urlpatterns = [
    path("search/<page>", views.search, name="search"),
    path("product/<item_id>", views.product, name="product"),
    path("update_item", views.updateItem, name="update_item")
]