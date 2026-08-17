from django.db import migrations, models


def seed_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model("core", "PaymentMethod")
    defaults = ["Visa", "Mastercard", "Elo", "Hipercard", "Diners"]
    for i, name in enumerate(defaults):
        PaymentMethod.objects.get_or_create(name=name, defaults={"order": i, "active": True})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_fix_hours_and_maps_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Ex: Visa, Mastercard, Elo, Pix...", max_length=40, verbose_name="Nome")),
                ("active", models.BooleanField(default=True, verbose_name="Ativo")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Ordem")),
            ],
            options={
                "verbose_name": "Forma de pagamento",
                "verbose_name_plural": "Formas de pagamento",
                "ordering": ["order", "name"],
            },
        ),
        migrations.RunPython(seed_payment_methods, noop),
    ]
