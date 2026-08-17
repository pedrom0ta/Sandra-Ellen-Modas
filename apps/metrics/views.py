"""
Views do app de métricas:
- whatsapp_redirect: endpoint público (sem login) que registra o clique e
  redireciona para o WhatsApp. Validação estrita de destino evita que vire
  um open redirect.
- metrics_dashboard: página "Métricas" dentro do admin (staff only).

O dashboard foi desenhado para quem NÃO entende de analytics: o foco é um
único ranking simples — quais produtos as pessoas mais acessam e quantas
vezes clicaram em "Falar no WhatsApp" a partir deles. Nada de taxa de
conversão, médias, gráficos de evolução ou jargão técnico.
"""
from datetime import timedelta
from urllib.parse import urlparse

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Count
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from apps.catalog.models import Product
from apps.core.utils import anonymize_ip, get_client_ip

from .models import ProductView, WhatsAppClick

# ---------------------------------------------------------------------------
# Redirecionador do WhatsApp
# ---------------------------------------------------------------------------
ALLOWED_REDIRECT_HOST = "wa.me"


def whatsapp_redirect(request):
    """
    Registra o clique e redireciona para o WhatsApp.

    Só GET, e só redireciona para https://wa.me/... — nunca confiamos
    cegamente no parâmetro `to`, ou esse endpoint viraria um open redirect
    utilizável para phishing.
    """
    target = request.GET.get("to", "")
    parsed = urlparse(target)
    if parsed.scheme != "https" or parsed.netloc != ALLOWED_REDIRECT_HOST:
        return HttpResponseBadRequest("Destino inválido.")

    product = None
    product_id = request.GET.get("product_id", "")
    if product_id.isdigit():
        product = Product.objects.filter(pk=product_id).first()

    try:
        WhatsAppClick.objects.create(
            product=product,
            session_key=request.session.session_key or "",
            ip_address=anonymize_ip(get_client_ip(request)),
            source_path=request.META.get("HTTP_REFERER", "")[:300],
        )
    except Exception:
        # Mesmo se o registro da métrica falhar, o cliente TEM que chegar ao WhatsApp.
        pass

    return HttpResponseRedirect(target)


# ---------------------------------------------------------------------------
# Dashboard "Métricas" (dentro do admin) — ranking de produtos
# ---------------------------------------------------------------------------
DASHBOARD_CACHE_KEY = "metrics:dashboard:v4:{days}"
DASHBOARD_CACHE_TTL = 120  # 2 min — painel não precisa ser estritamente real-time

# dias -> rótulo mostrado no filtro. "Hoje" é só o dia 1 (hoje mesmo).
PERIOD_LABELS = {
    1: "Hoje",
    7: "7 dias",
    30: "30 dias",
}
PERIOD_CHOICES = tuple(PERIOD_LABELS.keys())
DEFAULT_PERIOD_DAYS = 30

TOP_PRODUCTS_LIMIT = 10


def _resolve_period_days(request):
    try:
        days = int(request.GET.get("days", DEFAULT_PERIOD_DAYS))
    except (TypeError, ValueError):
        days = DEFAULT_PERIOD_DAYS
    return days if days in PERIOD_CHOICES else DEFAULT_PERIOD_DAYS


def _build_dashboard_data(days):
    now = timezone.localtime()
    today = now.date()
    period_start = today - timedelta(days=days - 1)

    views_qs = ProductView.objects.filter(
        created_at__date__gte=period_start, created_at__date__lte=today
    )
    clicks_qs = WhatsAppClick.objects.filter(
        created_at__date__gte=period_start, created_at__date__lte=today
    )

    # ---------------- Contadores gerais (bem diretos, sem taxas nem médias) ----
    total_product_views = views_qs.count()
    total_whatsapp_clicks = clicks_qs.count()

    # ---------------- Ranking de produtos mais acessados -----------------------
    views_rows = list(
        views_qs.values("product_id", "product__name").annotate(views=Count("id"))
    )
    clicks_by_product = dict(
        clicks_qs.filter(product__isnull=False)
        .values("product_id")
        .annotate(clicks=Count("id"))
        .values_list("product_id", "clicks")
    )

    top_products = sorted(views_rows, key=lambda r: -r["views"])[:TOP_PRODUCTS_LIMIT]
    max_views = top_products[0]["views"] if top_products else 0

    # Busca os objetos Product só dos itens do ranking, para pegar a foto
    # principal real cadastrada (product.main_image.url) — evitado no
    # queryset de agregação acima porque ali trabalhamos só com .values().
    products_by_id = Product.objects.in_bulk([r["product_id"] for r in top_products])

    for position, item in enumerate(top_products, start=1):
        item["rank"] = position
        item["clicks"] = clicks_by_product.get(item["product_id"], 0)
        # Só usado para desenhar a barrinha proporcional ao lado do nome —
        # não é exibido como número/porcentagem na tela.
        item["bar_pct"] = round((item["views"] / max_views) * 100, 1) if max_views else 0

        product_obj = products_by_id.get(item["product_id"])
        item["image_url"] = product_obj.main_image.url if product_obj and product_obj.main_image else ""

    # ---------------- Destaque: produto mais acessado do período ---------------
    top_product = None
    if top_products:
        top = top_products[0]
        top_product = {
            "product_id": top["product_id"],
            "name": top["product__name"],
            "views": top["views"],
            "clicks": top["clicks"],
            "image_url": top["image_url"],
        }

    return {
        "period_days": days,
        "period_start": period_start,
        "period_end": today,
        "total_product_views": total_product_views,
        "total_whatsapp_clicks": total_whatsapp_clicks,
        "top_product": top_product,
        "top_products": top_products,
        "generated_at": now,
    }


@staff_member_required
def metrics_dashboard(request):
    days = _resolve_period_days(request)
    cache_key = DASHBOARD_CACHE_KEY.format(days=days)
    data = cache.get(cache_key)
    if data is None:
        data = _build_dashboard_data(days)
        cache.set(cache_key, data, DASHBOARD_CACHE_TTL)

    context = {
        **admin.site.each_context(request),
        **data,
        "period_choices": [{"days": d, "label": PERIOD_LABELS[d]} for d in PERIOD_CHOICES],
        "title": "Métricas",
    }
    return render(request, "admin/metrics/dashboard.html", context)
