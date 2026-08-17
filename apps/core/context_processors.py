from .models import StoreInfo, StoreHour, PaymentMethod

WEEKDAY_SHORT_NAMES = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def _grouped_store_hours():
    """Agrupa dias consecutivos com o mesmo horário (ex: Segunda à Sexta)."""
    hours = list(StoreHour.objects.all().order_by("weekday"))
    groups = []
    for h in hours:
        key = (h.opens_at, h.closes_at, h.closed)
        if groups and groups[-1]["key"] == key and groups[-1]["last_weekday"] == h.weekday - 1:
            groups[-1]["last_weekday"] = h.weekday
        else:
            groups.append({"key": key, "first_weekday": h.weekday, "last_weekday": h.weekday})

    result = []
    for g in groups:
        first, last = g["first_weekday"], g["last_weekday"]
        label = WEEKDAY_SHORT_NAMES[first] if first == last else f"{WEEKDAY_SHORT_NAMES[first]} à {WEEKDAY_SHORT_NAMES[last]}"
        opens_at, closes_at, closed = g["key"]
        text = "Fechado" if closed else f"{opens_at.strftime('%H:%M')} às {closes_at.strftime('%H:%M')}"
        result.append({"label": label, "text": text})
    return result


def site_settings(request):
    return {
        "store": StoreInfo.load(),
        "store_hours": StoreHour.objects.all(),
        "grouped_hours": _grouped_store_hours(),
        "payment_methods": PaymentMethod.objects.filter(active=True),
    }
