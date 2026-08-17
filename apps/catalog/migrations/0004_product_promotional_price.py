from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_alter_product_main_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="promotional_price",
            field=models.DecimalField(
                blank=True,
                null=True,
                max_digits=10,
                decimal_places=2,
                verbose_name="Preço promocional",
                help_text="Preencha apenas se a peça estiver em promoção. Deve ser menor que o preço normal.",
            ),
        ),
    ]
