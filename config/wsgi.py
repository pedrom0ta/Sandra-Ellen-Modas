"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Na Vercel, a variável de sistema VERCEL=1 é injetada automaticamente
# tanto no build quanto em runtime. Localmente (sem essa variável),
# continua usando as settings de desenvolvimento como antes.
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.vercel' if os.environ.get('VERCEL') else 'config.settings.dev',
)

application = get_wsgi_application()
