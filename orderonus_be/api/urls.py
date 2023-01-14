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
    delete_dish,
    add_dish_modifier,
)

urlpatterns = [
    # Orders
    path("orders/", orders, name="orders"),
    path("orders/add", add_order, name="add_order"),
    path("orders/<int:order_id>/", order_by_id, name="order_by_id"),
    path("orders/<int:order_id>/complete", complete_order, name="complete_order"),
    # Dishes
    path("dishes/", get_dishes, name="get_dishes"),
    path("dishes/add", add_dishes, name="add_dishes"),
    path("dishes/<int:dish_id>/edit", edit_dish, name="edit_dish"),
    path("dishes/<int:dish_id>/delete", delete_dish, name="delete dish"),
    path("dishes/<int:dish_id>/available", available, name="available"),
    path("dishes/<int:dish_id>/modifier/add", add_dish_modifier, name="Add modifier"),
]
