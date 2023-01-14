import json
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login


# Create your views here.
@require_POST
def user_login(request: HttpRequest) -> HttpResponse:
    """Log in for the user"""
    post_dict = json.loads(request.body)
    username = post_dict.get("username", None)
    password = post_dict.get("password", None)

    if (None in [username, password]) or ("" in [username, password]):
        return JsonResponse({"error": "Username or password not provided"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"error": "User does not exist or Password is incorrect"}, status=404
        )

    login(request, user)

    return JsonResponse({"data": "User logged in successfully"}, status=200)


@require_POST
def user_register(request: HttpRequest) -> HttpResponse:
    """Register the user"""
    post_dict = json.loads(request.body)
    username = post_dict.get("username", None)
    password = post_dict.get("password", None)
    if (None in [username, password]) or ("" in [username, password]):
        return JsonResponse({"error": "Username or password not provided"}, status=400)

    user = User.objects.filter(username=username).first()
    if user is not None:
        return JsonResponse({"error": "User already exists"}, status=409)

    user = User.objects.create_user(username=username, password=password)
    user.save()

    return JsonResponse({"data": "User created successfully"}, status=201)
