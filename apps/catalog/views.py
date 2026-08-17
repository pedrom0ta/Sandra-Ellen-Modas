from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from apps.metrics.services import track_product_view

from .models import Product, Category, Brand

PAGE_SIZE = 12

ORDER_OPTIONS = {
    "recent": ("-created_at", "Mais recentes"),
    "price_asc": ("price", "Menor preço"),
    "price_desc": ("-price", "Maior preço"),
    "name": ("name", "Nome (A-Z)"),
}


def catalog_list(request):
    products = Product.objects.filter(active=True).select_related("brand", "category").prefetch_related("gallery")

    query = request.GET.get("q", "").strip()
    brand_slug = request.GET.get("marca", "")
    category_slug = request.GET.get("categoria", "")
    order_key = request.GET.get("ordenar", "recent")
    promo_only = request.GET.get("promo") == "1"

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query) | Q(short_description__icontains=query)
        )
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if promo_only:
        products = products.filter(promotional_price__isnull=False, promotional_price__lt=F("price"))

    order_field = ORDER_OPTIONS.get(order_key, ORDER_OPTIONS["recent"])[0]
    products = products.order_by(order_field)

    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    if request.GET.get("partial") == "1":
        html = render_to_string("catalog/_product_cards.html", {"page_obj": page_obj}, request=request)
        return JsonResponse({
            "html": html,
            "has_next": page_obj.has_next(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        "page_obj": page_obj,
        "brands": Brand.objects.filter(active=True),
        "categories": Category.objects.filter(active=True),
        "order_options": ORDER_OPTIONS,
        "current_query": query,
        "current_brand": brand_slug,
        "current_category": category_slug,
        "current_order": order_key,
        "current_promo": promo_only,
        "meta_title": "Promoções — Sandra Ellen Modas" if promo_only else "Catálogo — Sandra Ellen Modas",
        "meta_description": (
            "Confira as peças em promoção da Sandra Ellen Modas em Araci - BA."
            if promo_only
            else "Confira as novidades e peças exclusivas do catálogo Sandra Ellen Modas em Araci - BA."
        ),
    }
    return render(request, "catalog/catalog_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("brand", "category"), slug=slug, active=True)
    track_product_view(request, product)
    related = (
        Product.objects.filter(category=product.category, active=True)
        .exclude(pk=product.pk)
        .select_related("brand")
        .prefetch_related("gallery")[:4]
    )
    context = {
        "product": product,
        "related_products": related,
        "meta_title": f"{product.display_title} — Sandra Ellen Modas",
        "meta_description": product.display_meta_description,
    }
    return render(request, "catalog/product_detail.html", context)
