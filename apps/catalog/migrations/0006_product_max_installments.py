from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_product_available_sizes"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="max_installments",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Em quantas vezes sem juros essa peça pode ser parcelada. Digite 1 para não exibir parcelamento no site.",
                verbose_name="Parcelamento sem juros (opcional)",
            ),
        ),
    ]
