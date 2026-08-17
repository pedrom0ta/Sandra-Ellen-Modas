from urllib.parse import quote

from django import template

register = template.Library()


@register.simple_tag
def whatsapp_link(product_name=None, product=None, number=None):
    """
    Monta o link do WhatsApp (mesmo comportamento de sempre) e devolve a URL
    já passando pelo redirecionador interno de métricas, que registra o
    clique antes de mandar o visitante pro WhatsApp de verdade.

    `product`: opcional, o objeto Product (não só o nome) — quando informado,
    permite contabilizar cliques por produto no painel de Métricas.
    """
    if not number:
        # Número e mensagem padrão vêm do Admin (Informações da loja),
        # não mais de variável de ambiente — assim dá pra trocar sem redeploy.
        from apps.core.models import StoreInfo
        store = StoreInfo.load()
        number = store.whatsapp_number
        default_message = store.whatsapp_default_message
    else:
        default_message = "Olá, gostaria de mais informações."

    if product_name:
        msg = f"Olá, tenho interesse na peça {product_name}"
    else:
        msg = default_message
    wa_url = f"https://wa.me/{number}?text={quote(msg)}"

    from apps.metrics.services import build_tracked_whatsapp_url
    return build_tracked_whatsapp_url(wa_url, product=product)


@register.filter
def brl(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


@register.filter
def initials(name):
    """Pega a primeira letra das duas primeiras palavras do nome. Ex: 'Vestido Midi' -> 'VM'."""
    if not name:
        return ""
    words = str(name).split()
    return "".join(w[0] for w in words[:2]).upper()


@register.filter
def placeholder_hue(product_id):
    """Gera um matiz (0-359) determinístico a partir do id, igual ao gerado na landing page."""
    try:
        return (int(product_id) * 47) % 360
    except (TypeError, ValueError):
        return 0
