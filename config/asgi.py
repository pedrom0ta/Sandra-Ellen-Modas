"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Como o projeto define tanto WSGI_APPLICATION quanto ASGI_APPLICATION,
# a Vercel prioriza o entrypoint ASGI — por isso esse arquivo também precisa
# resolver a settings module correta (mesma lógica do wsgi.py/manage.py).
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.vercel' if os.environ.get('VERCEL') else 'config.settings.dev',
)

application = get_asgi_application()
