from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.conf import settings
from django.views.static import serve

# Create your views here.
def homepage(_: HttpRequest) -> HttpResponse:
    """Home page to check server liveness"""
    return JsonResponse({"message": "Server is up and running"})


def serve_static(request: HttpRequest, path: str) -> HttpResponse:
    """Serve static files"""
    print(f"Requesting static file: {path}")
    return serve(request, path, document_root=settings.STATIC_ROOT)
