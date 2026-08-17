import os
import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .utils import compress_image
from .validators import validate_image_file


def _unique_slug(instance, base_value, slug_field="slug"):
    base_slug = slugify(base_value)[:180]
    Model = instance.__class__
    slug = base_slug
    n = 1
    qs = Model.objects.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: slug}).exists():
        n += 1
        slug = f"{base_slug}-{n}"
    return slug


def product_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"products/{uuid.uuid4().hex}{ext}"


class Category(models.Model):
    name = models.CharField("Nome", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    active = models.BooleanField("Ativa", default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField("Nome", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    logo = models.ImageField("Logo (opcional)", upload_to="brands/", blank=True, null=True, validators=[validate_image_file])
    order = models.PositiveIntegerField("Ordem de exibição", default=0, help_text="Marcas com número menor aparecem primeiro no site.")
    active = models.BooleanField("Ativa", default=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField("Nome", max_length=200)
    slug = models.SlugField("Slug (URL amigável)", max_length=220, unique=True, blank=True)
    brand = models.ForeignKey(Brand, verbose_name="Marca", on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, verbose_name="Categoria", on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField("Preço", max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(
        "Preço promocional", max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Preencha apenas se a peça estiver em promoção. Deve ser menor que o preço normal.",
    )
    max_installments = models.PositiveIntegerField(
        "Parcelamento sem juros (opcional)", default=1,
        help_text="Em quantas vezes sem juros essa peça pode ser parcelada. Digite 1 para não exibir parcelamento no site.",
    )
    short_description = models.CharField("Descrição curta", max_length=255)
    full_description = models.TextField("Descrição completa", blank=True)
    available_sizes = models.CharField(
        "Tamanhos disponíveis (opcional)", max_length=100, blank=True,
        help_text="Digite livremente, ex: P, M, G ou 36, 38, 40, 42.",
    )
    main_image = models.ImageField(
        "Imagem principal", upload_to=product_image_upload_to,
        validators=[validate_image_file], blank=True, null=True,
        help_text="Se não enviar imagem, o site mostra um card com as iniciais do produto.",
    )

    is_featured = models.BooleanField("Destaque", default=False)
    is_new = models.BooleanField("Novidade", default=False)
    is_bestseller = models.BooleanField("Mais vendido", default=False)
    active = models.BooleanField("Ativo", default=True)

    meta_title = models.CharField("Title (SEO, opcional)", max_length=70, blank=True)
    meta_description = models.CharField("Meta description (SEO, opcional)", max_length=160, blank=True)

    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["active", "-created_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.promotional_price is not None and self.price is not None:
            if self.promotional_price >= self.price:
                raise ValidationError({"promotional_price": "O preço promocional deve ser menor que o preço normal."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        if self.main_image and hasattr(self.main_image.file, "content_type"):
            # só recomprime quando é um upload novo (arquivo em memória), não ao apenas re-salvar
            try:
                self.main_image = compress_image(self.main_image)
            except Exception:
                pass  # se falhar a compressão, mantém o arquivo original validado
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def display_title(self):
        return self.meta_title or self.name

    @property
    def display_meta_description(self):
        return self.meta_description or self.short_description

    @property
    def is_on_promotion(self):
        return bool(self.promotional_price and self.promotional_price < self.price)

    @property
    def discount_percent(self):
        if not self.is_on_promotion:
            return 0
        return round((1 - (self.promotional_price / self.price)) * 100)

    @property
    def current_price(self):
        return self.promotional_price if self.is_on_promotion else self.price

    @property
    def has_installments(self):
        return self.max_installments and self.max_installments > 1

    @property
    def installment_value(self):
        if not self.has_installments:
            return None
        return self.current_price / self.max_installments


class ProductImage(models.Model):
    """Galeria de imagens adicionais do produto."""
    product = models.ForeignKey(Product, verbose_name="Produto", on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField("Imagem", upload_to=product_image_upload_to, validators=[validate_image_file])
    order = models.PositiveIntegerField("Ordem", default=0)
    alt_text = models.CharField("Texto alternativo (acessibilidade)", max_length=200, blank=True)

    class Meta:
        verbose_name = "Imagem da galeria"
        verbose_name_plural = "Imagens da galeria"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Imagem de {self.product.name} ({self.order})"

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image.file, "content_type"):
            try:
                self.image = compress_image(self.image)
            except Exception:
                pass
        super().save(*args, **kwargs)


