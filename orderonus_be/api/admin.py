from django.contrib import admin

# Register your models here.
from .models import Store, Dish, DishModifier, Order, OrderDishRelation


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "store", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    search_fields = ("id", "user__username", "store__name")


admin.site.register(Store)
admin.site.register(Dish)
admin.site.register(DishModifier)
admin.site.register(Order)
admin.site.register(OrderDishRelation)
