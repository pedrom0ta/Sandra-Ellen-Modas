from django.shortcuts import render

from apps.catalog.models import Product, Brand, Category


def home(request):
    # Prioriza destaques, mas completa com os mais recentes até ter peças
    # suficientes para os filtros da vitrine da home fazerem sentido.
    catalog_products = (
        Product.objects.filter(active=True)
        .select_related("brand", "category")
        .prefetch_related("gallery")
        .order_by("-is_featured", "-created_at")[:12]
    )

    context = {
        "featured_products": catalog_products,
        "brands": Brand.objects.filter(active=True)[:4],
        "catalog_brands": Brand.objects.filter(active=True, products__in=catalog_products).distinct(),
        "catalog_categories": Category.objects.filter(active=True, products__in=catalog_products).distinct(),
    }
    return render(request, "home.html", context)
