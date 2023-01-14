"""orderonus_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (
    orders,
    complete_order,
    available,
    add_order,
    get_dishes,
    add_dishes,
    edit_dish,
    order_by_id,
)

urlpatterns = [
    path("orders/", orders, name="orders"),
    path("complete_order/", complete_order, name="complete_order"),
    path("available/", available, name="available"),
    path("add_order/", add_order, name="add_order"),
    path("get_dishes/", get_dishes, name="get_dishes"),
    path("add_dishes/", add_dishes, name="add_dishes"),
    path("edit_dish/<int:dish_id>/", edit_dish, name="edit_dish"),
    path("orders/<int:order_id>/", order_by_id, name="order_by_id"),
]
