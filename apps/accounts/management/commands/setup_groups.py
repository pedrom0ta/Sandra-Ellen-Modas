from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLES = {
    "Administrador": None,  # recebe todas as permissões (equivalente a staff completo)
    "Editor": [
        "add_product", "change_product", "delete_product", "view_product",
        "add_productimage", "change_productimage", "delete_productimage", "view_productimage",
        "add_category", "change_category", "view_category",
        "add_brand", "change_brand", "view_brand",
        "change_storeinfo", "view_storeinfo",
        "add_storehour", "change_storehour", "view_storehour",
    ],
    "Funcionário": [
        "view_product", "view_category", "view_brand",
        "change_product",  # pode atualizar estoque/preço, mas não excluir
    ],
}


class Command(BaseCommand):
    help = "Cria os grupos de permissão Administrador, Editor e Funcionário."

    def handle(self, *args, **options):
        for role, codenames in ROLES.items():
            group, created = Group.objects.get_or_create(name=role)
            if codenames is None:
                perms = Permission.objects.all()
            else:
                perms = Permission.objects.filter(codename__in=codenames)
            group.permissions.set(perms)
            status = "criado" if created else "atualizado"
            self.stdout.write(self.style.SUCCESS(f"Grupo '{role}' {status} com {perms.count()} permissões."))
