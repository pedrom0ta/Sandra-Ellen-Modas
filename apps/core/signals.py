import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog
from .utils import get_client_ip as _client_ip

audit_logger = logging.getLogger("sandraellen.audit")


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    AuditLog.objects.create(user=user, action="login", ip_address=_client_ip(request))
    audit_logger.info("Login: %s", user.username)


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(user=user, action="logout", ip_address=_client_ip(request))
        audit_logger.info("Logout: %s", user.username)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    ip = _client_ip(request) if request else None
    AuditLog.objects.create(
        action="login_failed",
        object_repr=credentials.get("username", ""),
        ip_address=ip,
    )
    audit_logger.warning("Falha de login para usuário '%s'", credentials.get("username", ""))


# Modelos auditados automaticamente (CRUD). Populado em apps.py ready().
AUDITED_MODELS = []


def register_audited_model(model):
    AUDITED_MODELS.append(model)

    @receiver(post_save, sender=model, weak=False)
    def _on_save(sender, instance, created, **kwargs):
        AuditLog.objects.create(
            action="create" if created else "update",
            object_repr=f"{sender.__name__}: {instance}",
        )

    @receiver(post_delete, sender=model, weak=False)
    def _on_delete(sender, instance, **kwargs):
        AuditLog.objects.create(
            action="delete",
            object_repr=f"{sender.__name__}: {instance}",
        )
