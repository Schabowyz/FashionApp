from django.urls import path
from . import views

app_name = "items"
urlpatterns = [
    path("<page>", views.search, name="search"),
    path("product/<item_id>", views.product, name="product")
]