from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("politica-de-privacidade/", views.privacy_policy, name="privacy"),
    path("politica-de-cookies/", views.cookie_policy, name="cookies"),
    path("termos-de-uso/", views.terms_of_use, name="terms"),
]
