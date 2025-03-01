from django.urls import path

from . import views

urlpatterns = [
    path("", views.ApiHome, name="Home"),
    path("input/", views.input, name="input")
]