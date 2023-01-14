from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse

# Create your views here.
def homepage(_: HttpRequest) -> HttpResponse:
    """Home page to check server liveness"""
    return JsonResponse({"message": "Server is up and running"})
