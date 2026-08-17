from django.db import migrations


def update_store_info(apps, schema_editor):
    StoreInfo = apps.get_model("core", "StoreInfo")
    StoreHour = apps.get_model("core", "StoreHour")

    # Link oficial gerado pelo Google Maps (Compartilhar > Incorporar um mapa),
    # não exige chave de API e não sofre bloqueio de X-Frame-Options.
    # Só atualiza este campo (não mexe em instagram_url, facebook_url etc.
    # que possam já ter sido editados no admin).
    StoreInfo.objects.filter(pk=1).update(
        google_maps_embed_url=(
            "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3911.959594158063"
            "!2d-38.96331!3d-11.337662!3m2!1i1024!2i768!4f13.1!3m3!1m2"
            "!1s0x713c86d96da076b%3A0x64d524e1d582eefc"
            "!2sAv.%207%20de%20Setembro%2C%2028%2C%20Araci%20-%20BA%2C%2048760-000%2C%20Brasil"
            "!5e0!3m2!1spt-BR!2sus!4v1784691660444!5m2!1spt-BR!2sus"
        )
    )

    # Segunda à Sexta 09:00-18:00 | Sábado 09:00-12:00 | Domingo fechado
    hours = [
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
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_storeinfo_google_maps_embed_url"),
    ]

    operations = [
        migrations.RunPython(update_store_info, reverse_noop),
    ]
