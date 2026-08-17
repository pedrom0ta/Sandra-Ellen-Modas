from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Product, ProductImage


@receiver(pre_delete, sender=Product)
def delete_product_main_image(sender, instance, **kwargs):
    if instance.main_image:
        instance.main_image.delete(save=False)


@receiver(pre_delete, sender=ProductImage)
def delete_gallery_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
