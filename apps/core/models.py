from django.db import models


class StoreInfo(models.Model):
    """Singleton com dados institucionais da loja (editável no admin)."""
    name = models.CharField("Nome da loja", max_length=120, default="Sandra Ellen Modas")
    tagline = models.CharField("Chamada curta", max_length=200, blank=True)
    about_text = models.TextField("Texto 'Sobre'", blank=True)
    address = models.CharField("Endereço", max_length=255, blank=True)
    city = models.CharField("Cidade/UF", max_length=120, blank=True)
    zip_code = models.CharField("CEP", max_length=12, blank=True)
    phone = models.CharField("Telefone", max_length=30, blank=True)
    whatsapp_number = models.CharField(
        "WhatsApp (só números, com DDI+DDD)", max_length=20,
        help_text="Ex: 557532662033"
    )
    whatsapp_default_message = models.CharField(
        "Mensagem padrão do WhatsApp", max_length=255,
        default="Olá, gostaria de mais informações."
    )
    instagram_url = models.URLField("Instagram", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    google_maps_embed_url = models.URLField(
        "URL do mapa incorporado (Google Maps embed)", blank=True, max_length=500
    )
    meta_description = models.CharField("Meta description padrão (SEO)", max_length=160, blank=True)
    og_image = models.ImageField("Imagem Open Graph padrão", upload_to="site/", blank=True, null=True)
    google_analytics_id = models.CharField("Google Analytics ID", max_length=40, blank=True)
    meta_pixel_id = models.CharField("Meta Pixel ID", max_length=40, blank=True)

    topbar_enabled = models.BooleanField("Exibir faixa no topo do site", default=True)
    topbar_text = models.CharField(
        "Texto da faixa do topo", max_length=200, blank=True,
        default="Enviamos para todo o Brasil",
        help_text="Ex: Enviamos para todo o Brasil",
    )

    class Meta:
        verbose_name = "Informações da loja"
        verbose_name_plural = "Informações da loja"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1  # força singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"whatsapp_number": "557532662033"})
        return obj


class StoreHour(models.Model):
    WEEKDAYS = [
        (0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"),
        (3, "Quinta-feira"), (4, "Sexta-feira"), (5, "Sábado"), (6, "Domingo"),
    ]
    weekday = models.IntegerField("Dia da semana", choices=WEEKDAYS, unique=True)
    opens_at = models.TimeField("Abre às", null=True, blank=True)
    closes_at = models.TimeField("Fecha às", null=True, blank=True)
    closed = models.BooleanField("Fechado neste dia", default=False)

    class Meta:
        verbose_name = "Horário de funcionamento"
        verbose_name_plural = "Horários de funcionamento"
        ordering = ["weekday"]

    def __str__(self):
        if self.closed:
            return f"{self.get_weekday_display()}: Fechado"
        return f"{self.get_weekday_display()}: {self.opens_at} às {self.closes_at}"


class PaymentMethod(models.Model):
    """Bandeiras/formas de pagamento exibidas no rodapé (editável no admin)."""
    name = models.CharField("Nome", max_length=40, help_text="Ex: Visa, Mastercard, Elo, Pix...")
    active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Forma de pagamento"
        verbose_name_plural = "Formas de pagamento"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Trilha de auditoria: login, logout, CRUD, uploads, erros."""
    ACTION_CHOICES = [
        ("login", "Login"), ("logout", "Logout"), ("login_failed", "Falha de login"),
        ("create", "Criação"), ("update", "Edição"), ("delete", "Exclusão"),
        ("upload", "Upload"), ("error", "Erro"),
    ]
    user = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_repr = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de auditoria"
        verbose_name_plural = "Logs de auditoria"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%d/%m/%Y %H:%M} · {self.get_action_display()} · {self.user}"
