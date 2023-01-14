import json
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from .models import Order, OrderDishRelation, Dish, DishModifier, Store
from .utils import get_store
from typing import List


# Create your views here.
@require_GET
@login_required
def orders(request: HttpRequest, store_id: int) -> HttpResponse:
    """Retrive the orders from the database"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

    # Gets the orders from the past day
    pending_orders = (
        Order.objects.filter(created_at__contains=now().date(), store=store)
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
def order_by_id(request: HttpRequest, store_id: int, order_id: int) -> HttpResponse:
    """Retrive the order by id from the database"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

    order_id: int = request.POST.get("order_id")
    order = Order.objects.filter(id=order_id, store=store).get()
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
def complete_order(request: HttpRequest, store_id: int, order_id: int) -> HttpResponse:
    """Mark the order as complete"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

    post_dict = json.loads(request.body)
    is_completed = post_dict.get("is_completed", None)
    if is_completed is None:
        return JsonResponse({"error": "Missing parameter"}, status=400)
    try:
        order = Order.objects.filter(id=order_id, store=store).get()
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    order.is_completed = is_completed
    order.save()

    return JsonResponse({"data": "Order updated successfully"})


@require_POST
@login_required
def available(request: HttpRequest, store_id: int, dish_id: int) -> HttpResponse:
    """Mark the dish as available / unavailable"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

    post_dict = json.loads(request.body)
    is_available = post_dict.get("is_available", None)

    if is_available is None:
        return JsonResponse({"error": "Missing parameter"}, status=400)

    try:
        dish = Dish.objects.filter(id=dish_id, store=store).get()
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    dish.is_available = is_available
    dish.save()
    return JsonResponse({"data": "Dish updated successfully"})


@require_POST
@login_required
def add_order(request: HttpRequest, store_id: int) -> HttpResponse:
    """Adds the order to the database"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

    post_dict = json.loads(request.body)
    isOnline = post_dict.get("isOnline", False)
    isCompleted = post_dict.get("isCompleted", False)
    dishes = post_dict.get("dishes", None)
    if dishes is None:
        return JsonResponse({"error": "Missing parameter"}, status=400)

    if len(dishes) == 0:
        return JsonResponse({"error": "No dishes in order"}, status=400)

    order = Order.objects.create(
        is_online=isOnline,
        is_completed=isCompleted,
        store=store,
        created_at=now(),
    )
    relations: List[OrderDishRelation] = []
    for dish in dishes:
        try:
            dish_obj = Dish.objects.filter(id=dish.get("id")).get()
        except Dish.DoesNotExist:
            return JsonResponse({"error": "Dish not found"}, status=404)

        modifiers = dish.get("modifier", [])
        mods = list(
            map(
                lambda x: DishModifier.objects.filter(dish=dish_obj, id=x).get(),
                modifiers,
            )
        )
        quantity = dish.get("quantity", None)
        if quantity is None:
            return JsonResponse({"error": "Missing parameter"}, status=400)
        relation = OrderDishRelation.objects.create(
            order=order,
            dish=dish_obj,
            quantity=dish.get("quantity"),
            other_comments=dish.get("other_comments", ""),
        )
        relation.modifiers.set(mods)
        relations.append(relation)

    order.save()
    for r in relations:
        r.save()

    return JsonResponse({"data": "Order added successfully"})


@require_GET
@login_required
def get_dishes(request: HttpRequest, store_id: int) -> HttpResponse:
    """Gets the possible dishes"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)
    return JsonResponse(
        {
            "data": list(
                map(lambda x: x.to_dict(), Dish.objects.filter(store=store).all())
            )
        }
    )


@require_POST
@login_required
def add_dishes(request: HttpRequest, store_id: int) -> HttpResponse:
    """Creates a new dish and adds it into the database"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)

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
        store=store,
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
def edit_dish(request: HttpRequest, store_id: int, dish_id: int) -> HttpResponse:
    """Edits the dish"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)
    try:
        dish = Dish.objects.get(id=dish_id, store=store)
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
def delete_dish(request: HttpRequest, store_id: int, dish_id: int) -> HttpResponse:
    """Deletes the dish"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)
    try:
        dish = Dish.objects.get(id=dish_id, store=store)
    except Dish.DoesNotExist:
        return JsonResponse({"error": "Dish not found"}, status=404)

    dish.delete()
    return JsonResponse({"data": "Dish deleted successfully"})


@require_POST
@login_required
def add_dish_modifier(
    request: HttpRequest, store_id: int, dish_id: int
) -> HttpResponse:
    """Adds a modifier to the dish"""
    store = get_store(request.user, store_id)
    if store is None:
        return JsonResponse({"error": "Store not found"}, status=404)
    try:
        dish = Dish.objects.get(id=dish_id, store=store)
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


@require_GET
@login_required
def get_stores(request: HttpRequest) -> HttpResponse:
    """Gets the stores"""
    return JsonResponse({"data": list(map(lambda x: x.to_dict(), Store.objects.all()))})


@require_POST
@login_required
def add_store(request: HttpRequest) -> HttpResponse:
    """Adds a store"""
    post_dict = json.loads(request.body)
    name = post_dict.get("name", None)
    image = post_dict.get("image", None)
    description = post_dict.get("description", "")

    if name is None:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    if Store.objects.filter(name=name).exists():
        return JsonResponse({"error": "Store already exists"}, status=400)

    store = Store.objects.create(
        name=name,
        image=image,
        description=description,
        user=request.user,
    )
    store.save()

    return JsonResponse({"data": "Store added successfully"})
