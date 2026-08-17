from django.contrib import admin
from django.urls import path

from .views import metrics_dashboard

# ---------------------------------------------------------------------------
# Página customizada "Métricas" — padrão recomendado pelo Django para
# adicionar telas fora do CRUD padrão de um ModelAdmin: estender
# AdminSite.get_urls(). admin.site.admin_view() garante a mesma proteção
# (login + is_staff) de qualquer outra tela do admin.
# ---------------------------------------------------------------------------
_original_get_urls = admin.site.get_urls


def _get_urls_with_metrics():
    custom_urls = [
        path("metricas/", admin.site.admin_view(metrics_dashboard), name="metrics_dashboard"),
    ]
    return custom_urls + _original_get_urls()


admin.site.get_urls = _get_urls_with_metrics


# ---------------------------------------------------------------------------
# Propositalmente SEM admin.site.register() para Visit, ProductView e
# WhatsAppClick: essas tabelas não aparecem mais como itens separados no
# menu/sidebar do admin. Isso é só uma questão de interface — os modelos, os
# dados e a coleta continuam existindo normalmente (middleware.py e
# services.py continuam gravando neles), e o dashboard de Métricas
# (metrics_dashboard, em views.py) continua consultando essas mesmas tabelas
# via ORM diretamente, sem depender de registro no admin.
# ---------------------------------------------------------------------------
