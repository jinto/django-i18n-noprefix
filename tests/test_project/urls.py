"""
URL configuration for test project.
"""

from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path


def home_view(request):
    """Simple home view for testing."""
    return HttpResponse("Home")


def about_view(request):
    """Simple about view for testing."""
    return HttpResponse("About")


def contact_view(request):
    """Simple contact view for testing."""
    return HttpResponse("Contact")


def api_data_view(request):
    """Simple API endpoint for testing."""
    return JsonResponse({"data": "test", "language": request.LANGUAGE_CODE})


def products_detail_view(request, product_id):
    """Product detail view for testing deep linking."""
    return HttpResponse(f"Product {product_id}")


urlpatterns = [
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("api/data/", api_data_view, name="api-data"),
    path("products/<int:product_id>/", products_detail_view, name="product-detail"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django_i18n_noprefix.urls", namespace="i18n")),
]
