import json
from datetime import datetime

from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from .models import Order, OrderDishRelation, Dish, DishModifier


# Create your views here.
@require_GET
@login_required
def orders(_: HttpRequest) -> HttpResponse:
    """Retrive the orders from the database"""

    # Gets the orders from the past day
    pending_orders = (
        Order.objects.filter(created_at__contains=datetime.today().date())
        .order_by("created_at")
        .all()
    )
    return JsonResponse(
        {
            "data": list(map(lambda x: x.to_dict(), pending_orders)),
        }
    )


@require_GET
@login_required
def order_by_id(request: HttpRequest, order_id: int) -> HttpResponse:
    """Retrive the order by id from the database"""
    order_id: int = request.POST.get("order_id")
    order = Order.objects.get(id=order_id)
    if order is None:
        return JsonResponse({"error": "Order not found"}, status=404)

    # Get the dishes in the order
    dishes = OrderDishRelation.objects.filter(order=order).all()
    return JsonResponse(
        {
            "data": {
                "order": order.to_dict(),
                "dishes": list(map(lambda x: x.to_dict(), dishes)),
            }
        }
    )


@require_POST
@login_required
def complete_order(request: HttpRequest, order_id: int) -> HttpResponse:
    """Mark the order as complete"""
    post_dict = json.loads(request.body)
    is_completed = post_dict.get("is_completed", None)
    if is_completed is None:
        return JsonResponse({"error": "Missing parameter"}, status=400)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    order.is_completed = is_completed
    order.save()

    return JsonResponse({"data": "Order updated successfully"})


@require_POST
@login_required
def available(request: HttpRequest, dish_id: int) -> HttpResponse:
    """Mark the dish as available / unavailable"""
    post_dict = json.loads(request.body)
    is_available = post_dict.get("is_available", None)

    if is_available is None:
        return JsonResponse({"error": "Missing parameter"}, status=400)

    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    dish.is_available = is_available
    dish.save()
    return JsonResponse({"data": "Dish updated successfully"})


@require_POST
@login_required
def add_order(request: HttpRequest) -> HttpResponse:
    """Adds the order to the database"""
    # TODO Complete add order API.
    return JsonResponse()


@require_GET
@login_required
def get_dishes(request: HttpRequest) -> HttpResponse:
    """Gets the possible dishes"""
    return JsonResponse({"data": list(map(lambda x: x.to_dict(), Dish.objects.all()))})


@require_POST
@login_required
def add_dishes(request: HttpRequest) -> HttpResponse:
    """Creates a new dish and adds it into the database"""
    post_dict = json.loads(request.body)
    name = post_dict.get("name", None)
    price = post_dict.get("price", None)
    description = post_dict.get("description", "")
    image = post_dict.get("image", None)
    is_available = post_dict.get("is_available", True)
    modifiers = post_dict.get("modifiers", [])

    if None in [name, price] or name == "":
        return JsonResponse(
            {"error": "Invalid request, please have a valid name"},
            status=400,
        )

    if Dish.objects.filter(name=name).exists():
        return JsonResponse(
            {"error": "Dish already exists, please use a different name"}, status=400
        )

    dish = Dish.objects.create(
        name=name,
        price=price,
        description=description,
        image=image,
        is_available=is_available,
    )
    mod_objs = []
    for modifier in modifiers:
        mod = DishModifier.objects.create(
            dish=dish, name=modifier.get("name"), price=modifier.get("price", 0)
        )
        mod_objs.append(mod)

    for mod in mod_objs:
        mod.save()
    dish.save()

    return JsonResponse({"data": "Dish created successfully"})


@require_POST
@login_required
def edit_dish(request: HttpRequest, dish_id: int) -> HttpResponse:
    """Edits the dish"""
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    post_dict = json.loads(request.body)
    name = post_dict.get("name", None)
    if name is not None:
        dish.name = name
    price = post_dict.get("price", None)
    if price is not None:
        dish.price = price
    description = post_dict.get("description", None)
    if description is not None:
        dish.description = description
    image = post_dict.get("image", None)
    if image is not None:
        dish.image = image
    dish.save()
    return JsonResponse({"data": "Dish updated successfully"})


@require_POST
@login_required
def delete_dish(request: HttpRequest, dish_id: int) -> HttpResponse:
    """Deletes the dish"""
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    dish.delete()
    return JsonResponse({"data": "Dish deleted successfully"})


@require_POST
@login_required
def add_dish_modifier(request: HttpRequest, dish_id: int) -> HttpResponse:
    """Adds a modifier to the dish"""
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    post_dict = json.loads(request.body)
    name = post_dict.get("name", None)
    price = post_dict.get("price", None)
    is_available = post_dict.get("is_available", True)
    if None in [name, price]:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    modifier = DishModifier.objects.create(
        dish=dish,
        name=name,
        price=price,
        is_available=is_available,
    )
    modifier.save()
    return JsonResponse({"data": "Modifier added successfully"})
