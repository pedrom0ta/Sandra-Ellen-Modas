"""
Modelos do painel de métricas.

Filosofia de gravação: nenhuma tabela aqui grava 1 linha por requisição HTTP.
A camada de dedupe (ver apps/metrics/services.py e middleware.py) garante que
só escrevemos no Postgres quando é de fato um evento novo (visitante que
reapareceu depois da janela de dedupe, produto visto de novo depois de um
tempo, ou um clique real no WhatsApp). Isso mantém a tabela pequena e as
consultas de agregação do dashboard rápidas, mesmo sem um processo de
limpeza/expurgo de dados antigos.
"""
from django.db import models


class Visit(models.Model):
    """
    Uma "visita" = a chegada de um visitante (sessão) ao site, já filtrada
    pela janela de dedupe. Não é analytics de página-a-página: é o suficiente
    para responder "quantos visitantes distintos passaram pelo site".
    """
    session_key = models.CharField("Sessão", max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField("IP (anonimizado)", null=True, blank=True)
    user_agent = models.CharField("User-Agent", max_length=300, blank=True)
    path = models.CharField("Página de entrada", max_length=300, blank=True)
    created_at = models.DateTimeField("Quando", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["session_key", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.created_at:%d/%m/%Y %H:%M} · {self.path or '/'}"


class ProductView(models.Model):
    """Uma visualização de produto (já deduplicada por sessão/produto)."""
    product = models.ForeignKey(
        "catalog.Product", verbose_name="Produto",
        on_delete=models.CASCADE, related_name="metric_views",
    )
    session_key = models.CharField("Sessão", max_length=40, blank=True)
    ip_address = models.GenericIPAddressField("IP (anonimizado)", null=True, blank=True)
    created_at = models.DateTimeField("Quando", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Visualização de produto"
        verbose_name_plural = "Visualizações de produtos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.product} · {self.created_at:%d/%m/%Y %H:%M}"


class WhatsAppClick(models.Model):
    """Um clique em qualquer botão 'Falar no WhatsApp' do site."""
    product = models.ForeignKey(
        "catalog.Product", verbose_name="Produto (se aplicável)",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="whatsapp_clicks",
    )
    session_key = models.CharField("Sessão", max_length=40, blank=True)
    ip_address = models.GenericIPAddressField("IP (anonimizado)", null=True, blank=True)
    source_path = models.CharField("Página de origem", max_length=300, blank=True)
    created_at = models.DateTimeField("Quando", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Clique no WhatsApp"
        verbose_name_plural = "Cliques no WhatsApp"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["product", "-created_at"]),
        ]

    def __str__(self):
        alvo = self.product.name if self.product else "Geral"
        return f"{alvo} · {self.created_at:%d/%m/%Y %H:%M}"
