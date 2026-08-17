from django.db import migrations


def populate_store_info(apps, schema_editor):
    StoreInfo = apps.get_model("core", "StoreInfo")
    StoreHour = apps.get_model("core", "StoreHour")

    StoreInfo.objects.update_or_create(
        pk=1,
        defaults={
            "name": "Sandra Ellen Modas",
            "tagline": "As melhores marcas da moda feminina em Araci.",
            "about_text": "",
            "address": "Avenida Sete de Setembro, 28, Centro",
            "city": "Araci - BA",
            "zip_code": "48760-000",
            "phone": "(75) 3266-2033",
            "whatsapp_number": "557532662033",
            "whatsapp_default_message": "Olá, gostaria de mais informações.",
            "google_maps_embed_url": (
                "https://www.google.com/maps?q=Avenida+Sete+de+Setembro,+28,"
                "+Centro,+Araci+-+BA,+48760-000&output=embed"
            ),
        },
    )

    hours = [
        # weekday: 0=Segunda ... 6=Domingo
        (0, "09:00", "18:00", False),
        (1, "09:00", "18:00", False),
        (2, "09:00", "18:00", False),
        (3, "09:00", "18:00", False),
        (4, "09:00", "18:00", False),
        (5, "09:00", "12:00", False),
        (6, None, None, True),
    ]
    for weekday, opens_at, closes_at, closed in hours:
        StoreHour.objects.update_or_create(
            weekday=weekday,
            defaults={"opens_at": opens_at, "closes_at": closes_at, "closed": closed},
        )


def reverse_noop(apps, schema_editor):
    # Não removemos os dados no reverse — só a estrutura importa para rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_store_info, reverse_noop),
    ]
