from django.contrib import admin
from .models import StoreInfo, StoreHour, PaymentMethod, AuditLog


@admin.register(StoreInfo)
class StoreInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identidade", {"fields": ("name", "tagline", "about_text")}),
        ("Faixa do topo", {"fields": ("topbar_enabled", "topbar_text")}),
        ("Contato", {"fields": ("address", "city", "zip_code", "phone", "whatsapp_number", "whatsapp_default_message")}),
        ("Redes sociais", {"fields": ("instagram_url", "facebook_url", "google_maps_embed_url")}),
        ("SEO / Marketing", {"fields": ("meta_description", "og_image", "google_analytics_id", "meta_pixel_id")}),
    )

    def has_add_permission(self, request):
        # Singleton: só pode existir 1 registro
        return not StoreInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StoreHour)
class StoreHourAdmin(admin.ModelAdmin):
    list_display = ("get_weekday_display", "opens_at", "closes_at", "closed")
    ordering = ("weekday",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order")
    list_editable = ("active", "order")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "user", "object_repr", "ip_address")
    list_filter = ("action", "created_at")
    search_fields = ("object_repr", "user__username")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
