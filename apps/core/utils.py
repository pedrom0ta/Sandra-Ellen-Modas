def get_client_ip(request):
    """
    IP real do cliente por trás do Nginx.

    O Nginx do projeto é o único proxy entre o cliente e o Django (1 hop
    confiável), e sempre ANEXA o IP real no final do header X-Forwarded-For
    (proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;).
    Qualquer valor antes do último pode ter sido forjado pelo próprio
    cliente na requisição original, então nunca confiamos no primeiro.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR")


def anonymize_ip(ip):
    """
    Anonimiza um endereço IP truncando a parte que identifica o host,
    seguindo a prática de "IP anonymization" usada por ferramentas de
    analytics (mantém a localização aproximada, remove o identificador
    individual). IPv4: zera o último octeto. IPv6: mantém só os primeiros
    4 grupos (64 bits).
    """
    if not ip:
        return None
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:4]) + "::"
    parts = ip.split(".")
    if len(parts) == 4:
        parts[-1] = "0"
        return ".".join(parts)
    return ip
