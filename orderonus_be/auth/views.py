from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login


# Create your views here.
@require_POST
def user_login(request: HttpRequest) -> HttpResponse:
    """Log in for the user"""
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)

    if (None in [username, password]) or ("" in [username, password]):
        return JsonResponse(
            {"message": "Username or password not provided"}, status=400
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"message": "User does not exist or Password is incorrect"}, status=404
        )

    login(request, user)

    return JsonResponse({"message": "User logged in successfully"}, status=200)


@require_POST
def user_register(request: HttpRequest) -> HttpResponse:
    """Register the user"""
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    if (None in [username, password]) or ("" in [username, password]):
        return JsonResponse(
            {"message": "Username or password not provided"}, status=400
        )

    user = User.objects.filter(username=username).first()
    if user is not None:
        return JsonResponse({"message": "User already exists"}, status=409)

    user = User.objects.create_user(username=username, password=password)
    user.save()

    return JsonResponse({"message": "User created successfully"}, status=201)
