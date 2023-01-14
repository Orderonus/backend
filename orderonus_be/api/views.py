from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST


# Create your views here.
@require_GET
def orders(request: HttpRequest) -> HttpResponse:
    """Retrive the orders from the database"""
    return JsonResponse()


@require_GET
def order_by_id(request: HttpRequest, order_id: int) -> HttpResponse:
    """Retrive the order by id from the database"""
    return JsonResponse()


@require_POST
def complete_order(request: HttpRequest) -> HttpResponse:
    """Mark the order as complete"""
    return JsonResponse()


@require_POST
def available(request: HttpRequest) -> HttpResponse:
    """Mark the dish as available / unavailable"""
    return JsonResponse()


@require_POST
def add_order(request: HttpRequest) -> HttpResponse:
    """Adds the order to the database"""
    return JsonResponse()


@require_GET
def get_dishes(request: HttpRequest) -> HttpResponse:
    """Gets the possible dishes"""
    return JsonResponse()


@require_POST
def add_dishes(request: HttpRequest) -> HttpResponse:
    """Creates a new dish and adds it into the database"""
    return JsonResponse()


@require_POST
def edit_dish(request: HttpRequest, dish_id: int) -> HttpResponse:
    """Edits the dish"""
    return JsonResponse()
