import logging

audit_logger = logging.getLogger("sandraellen.audit")


class SecurityHeadersMiddleware:
    """
    Headers de segurança que o Django não define nativamente:
    CSP, Permissions-Policy, COEP, CORP.
    (HSTS, X-Content-Type-Options, X-Frame-Options e Referrer-Policy
    já vêm do SecurityMiddleware/settings em produção.)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://connect.facebook.net; "
            "frame-src 'self' https://www.google.com; "
            "connect-src 'self' https://www.google-analytics.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )
        response.setdefault("Content-Security-Policy", csp)
        response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        response.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.setdefault("X-Content-Type-Options", "nosniff")
        return response


class AuditLogMiddleware:
    """Loga erros 5xx não tratados. Login/logout/CRUD são logados via signals (apps/core/signals.py)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 500:
            audit_logger.error(
                "Erro %s em %s (usuário=%s)",
                response.status_code, request.path,
                getattr(request.user, "username", "anônimo"),
            )
        return response
