from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Brand, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ("preview", "image", "alt_text", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height:70px;border-radius:4px;" />', obj.image.url)
        return "—"
    preview.short_description = "Prévia"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "product_count")
    list_editable = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Produtos"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "slug", "active", "product_count")
    list_editable = ("order", "active")
    list_display_links = ("name",)
    ordering = ("order", "name")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Produtos"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "brand", "category", "price", "promo_display", "is_featured", "is_new", "is_bestseller", "active", "updated_at")
    list_editable = ("active", "is_featured", "is_new", "is_bestseller")
    list_filter = ("active", "brand", "category", "is_featured", "is_new", "is_bestseller")
    search_fields = ("name", "brand__name", "category__name", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    date_hierarchy = "created_at"
    autocomplete_fields = ("brand", "category")
    readonly_fields = ("created_at", "updated_at", "main_image_preview")

    fieldsets = (
        ("Identificação", {"fields": ("name", "slug", "brand", "category")}),
        ("Comercial", {"fields": ("price", "promotional_price", "max_installments", "available_sizes", "short_description", "full_description")}),
        ("Imagens", {"fields": ("main_image_preview", "main_image")}),
        ("Destaques", {"fields": ("is_featured", "is_new", "is_bestseller", "active")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )

    def promo_display(self, obj):
        if obj.is_on_promotion:
            return format_html(
                '<span style="color:#c0392b;font-weight:600;">-{}% (R$ {})</span>',
                obj.discount_percent, f"{obj.promotional_price:.2f}".replace(".", ","),
            )
        return "—"
    promo_display.short_description = "Promoção"

    def thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.main_image.url)
        return "—"
    thumbnail.short_description = "Imagem"

    def main_image_preview(self, obj):
        if obj.pk and obj.main_image:
            return format_html('<img src="{}" style="max-height:220px;border-radius:6px;" />', obj.main_image.url)
        return "Nenhuma imagem enviada ainda."
    main_image_preview.short_description = "Prévia atual"

    class Media:
        # Drag & drop + preview antes do upload no formulário do admin
        js = ("catalog/admin_upload.js",)
