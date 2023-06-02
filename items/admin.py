from django.contrib import admin

from .models import Item, Price

# Register your models here.
admin.site.register(Item)
admin.site.register(Price)