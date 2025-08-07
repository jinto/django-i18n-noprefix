"""
URL configuration for test project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django_i18n_noprefix.urls")),
]
