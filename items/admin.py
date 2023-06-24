from django.contrib import admin

from .models import Item

# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    fields = ("name", "gender", "category", "description", "image", "visibility", "current_price")
    list_display =["id", "name", "gender", "category", "image"]
    search_fields = ["name"]
    order = ("id", "name")

admin.site.register(Item, ItemAdmin)