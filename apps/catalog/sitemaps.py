from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(active=True)

    def location(self, obj):
        return f"{reverse('catalog:catalog_list')}?categoria={obj.slug}"


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["home", "catalog:catalog_list", "pages:privacy", "pages:cookies", "pages:terms"]

    def location(self, item):
        return reverse(item)
