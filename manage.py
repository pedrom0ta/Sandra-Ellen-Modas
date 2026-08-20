#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Na Vercel, a variável de sistema VERCEL=1 é injetada automaticamente
    # tanto no build quanto em runtime. Localmente (sem essa variável),
    # continua usando as settings de desenvolvimento como antes.
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'config.settings.vercel' if os.environ.get('VERCEL') else 'config.settings.dev',
    )
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
