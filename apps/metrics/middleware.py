"""
Middleware que registra visitantes do site (não do admin) de forma leve:
- 1 leitura de cache por requisição elegível (rápido, não toca o Postgres).
- 1 escrita no Postgres só quando é de fato uma visita nova (fora da janela
  de dedupe), o que na prática é raro comparado ao volume de requisições.
"""
from apps.core.utils import anonymize_ip, get_client_ip
from django.core.cache import cache

from .utils import VISIT_DEDUPE_SECONDS, visit_cache_key

# Prefixos que nunca contam como "visita" do site público: painel
# administrativo, arquivos estáticos/mídia e os próprios endpoints internos
# de métricas (senão o redirecionador do WhatsApp inflaria as visitas).
EXCLUDED_PATH_PREFIXES = ("/admin", "/static/", "/media/", "/m/")


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._track(request, response)
        return response

    def _track(self, request, response):
        if request.method != "GET":
            return
        if request.path.startswith(EXCLUDED_PATH_PREFIXES):
            return
        if response.status_code >= 400:
            return
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Paginação AJAX do catálogo etc. — não é uma "nova página vista".
            return

        try:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            if not session_key:
                return  # sessão indisponível (ex: backend de sessão fora do ar) — não quebra o request

            cache_key = visit_cache_key(session_key)
            if cache.get(cache_key):
                return
            cache.set(cache_key, True, VISIT_DEDUPE_SECONDS)

            from .models import Visit  # import tardio evita import circular

            Visit.objects.create(
                session_key=session_key,
                ip_address=anonymize_ip(get_client_ip(request)),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                path=request.path[:300],
            )
        except Exception:
            # Métricas nunca podem derrubar uma requisição real do site.
            pass
