from django.db import migrations
from django.utils.text import slugify


def populate(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    Category = apps.get_model("catalog", "Category")

    brand_names = ["LANÇA PERFUME EASY", "MY FAVORITE THINGS (MYFT)", "CHARRY"]
    for name in brand_names:
        Brand.objects.get_or_create(name=name, defaults={"slug": slugify(name), "active": True})

    category_names = ["Vestidos", "Blazers", "Conjuntos", "Blusas", "Saias", "Calças", "Casacos"]
    for name in category_names:
        Category.objects.get_or_create(name=name, defaults={"slug": slugify(name), "active": True})


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate, reverse_noop),
    ]
