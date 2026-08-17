from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Em dev, SQLite é mais simples (produção usa Postgres — ver prod.py)
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
