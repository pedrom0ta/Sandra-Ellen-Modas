#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Padrão para desenvolvimento local. Na Vercel, cadastre a Environment
    # Variable DJANGO_SETTINGS_MODULE=config.settings.vercel no painel do
    # projeto — como setdefault() só age quando a variável ainda não existe,
    # o valor da Vercel tem prioridade automaticamente sem precisar mexer
    # neste arquivo. (Não usamos um valor condicional aqui porque o
    # mecanismo da Vercel que lê este arquivo para descobrir o
    # DJANGO_SETTINGS_MODULE espera uma string literal simples.)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
