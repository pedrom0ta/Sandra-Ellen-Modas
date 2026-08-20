from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.views.static import serve as serve_static

from apps.catalog.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from apps.pages.views import robots_txt
from apps.core.views import home

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("", include("apps.catalog.urls")),
    path("", include("apps.pages.urls")),
    path("m/", include("apps.metrics.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG or getattr(settings, "SERVE_MEDIA", False):
    # OBS: não usamos o helper django.conf.urls.static.static() aqui porque
    # ele é um no-op quando DEBUG=False (mesmo com SERVE_MEDIA=True) — ver
    # django/conf/urls/static.py. Como a Vercel é serverless e não tem um
    # Nginx servindo /media/, montamos a rota manualmente com a view
    # django.views.static.serve para esta demonstração.
    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
            serve_static,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

admin.site.site_header = "Sandra Ellen Modas — Administração"
admin.site.site_title = "Sandra Ellen Modas"
admin.site.index_title = "Painel de Gestão"
