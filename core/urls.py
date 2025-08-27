# core/urls.py
from django.contrib import admin
from django.urls import path
from web.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),  # Django root
]
