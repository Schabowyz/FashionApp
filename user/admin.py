from django.contrib import admin

from .models import UserAddress, Order, OrderedItems

# Register your models here.
admin.site.register(UserAddress)
admin.site.register(Order)
admin.site.register(OrderedItems)