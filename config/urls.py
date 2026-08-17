from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Sandra Ellen Modas — Administração"
admin.site.site_title = "Sandra Ellen Modas"
admin.site.index_title = "Painel de Gestão"
