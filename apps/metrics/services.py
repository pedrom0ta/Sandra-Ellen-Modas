"""
Camada de serviço do app de métricas: funções reutilizáveis chamadas a partir
de outros apps (catalog, templatetags). Mantém a lógica de rastreamento fora
das views de negócio, então o app catalog só precisa de 1 chamada de função.
"""
from urllib.parse import quote

from django.core.cache import cache
from django.urls import reverse

from apps.core.utils import anonymize_ip, get_client_ip

from .utils import PRODUCT_VIEW_DEDUPE_SECONDS, product_view_cache_key


def track_product_view(request, product):
    """
    Registra uma visualização de produto, deduplicada por sessão (ou IP, se
    não houver sessão) dentro de PRODUCT_VIEW_DEDUPE_SECONDS. Silenciosa e
    tolerante a falha: uma métrica nunca pode derrubar a página do produto.
    """
    from .models import ProductView  # import tardio evita import circular em apps.ready()

    try:
        session_key = request.session.session_key or ""
        fingerprint = session_key or get_client_ip(request) or "anon"
        cache_key = product_view_cache_key(fingerprint, product.pk)
        if cache.get(cache_key):
            return
        cache.set(cache_key, True, PRODUCT_VIEW_DEDUPE_SECONDS)

        ProductView.objects.create(
            product=product,
            session_key=session_key,
            ip_address=anonymize_ip(get_client_ip(request)),
        )
    except Exception:
        # Métricas são um "extra": nunca devem quebrar a navegação do cliente.
        pass


def build_tracked_whatsapp_url(wa_url: str, product=None) -> str:
    """
    Envolve uma URL wa.me com o redirecionador interno de métricas, para que
    o clique seja registrado antes do visitante sair para o WhatsApp.
    """
    url = reverse("metrics:whatsapp_redirect") + f"?to={quote(wa_url, safe='')}"
    if product is not None:
        url += f"&product_id={product.pk}"
    return url
