from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("catalogo/", views.catalog_list, name="catalog_list"),
    path("produto/<slug:slug>/", views.product_detail, name="product_detail"),
]
