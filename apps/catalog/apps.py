from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Catálogo"

    def ready(self):
        from . import signals  # noqa: F401
        from apps.core.signals import register_audited_model
        from .models import Product, Category, Brand

        for model in (Product, Category, Brand):
            register_audited_model(model)
