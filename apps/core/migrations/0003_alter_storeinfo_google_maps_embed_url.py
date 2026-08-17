from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_populate_store_info"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storeinfo",
            name="google_maps_embed_url",
            field=models.URLField(
                "URL do mapa incorporado (Google Maps embed)",
                blank=True,
                max_length=500,
            ),
        ),
    ]
