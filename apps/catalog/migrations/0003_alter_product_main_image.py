import apps.catalog.models
import apps.catalog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_populate_brands_categories"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="main_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.catalog.models.product_image_upload_to,
                validators=[apps.catalog.validators.validate_image_file],
                verbose_name="Imagem principal",
                help_text="Se não enviar imagem, o site mostra um card com as iniciais do produto.",
            ),
        ),
    ]
