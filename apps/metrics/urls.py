from django.urls import path

from . import views

app_name = "metrics"

urlpatterns = [
    path("ir/whatsapp/", views.whatsapp_redirect, name="whatsapp_redirect"),
]
