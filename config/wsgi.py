"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Padrão para desenvolvimento local. Na Vercel, cadastre a Environment
# Variable DJANGO_SETTINGS_MODULE=config.settings.vercel no painel do
# projeto — setdefault() só age quando a variável ainda não existe, então
# o valor da Vercel tem prioridade automaticamente (ver manage.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_wsgi_application()
