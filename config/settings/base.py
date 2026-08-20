"""
Configurações base — Sandra Ellen Modas
Compartilhadas por dev/homolog/produção. Nada de segredo aqui: tudo vem do .env.
"""
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",

    # apps do projeto
    "apps.core",
    "apps.catalog",
    "apps.pages",
    "apps.accounts",
    "apps.metrics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.AuditLogMiddleware",
    "apps.metrics.middleware.VisitorTrackingMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="sandraellen"),
        "USER": config("DB_USER", default="sandraellen"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# ---------------------------------------------------------------------------
# Senhas — Argon2 primeiro na lista = usado para novos hashes
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Bahia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Serve /media/ diretamente pelo Django mesmo com DEBUG=False.
# Necessário em ambientes serverless (Vercel) onde não existe um Nginx na
# frente do Django para servir os arquivos de mídia estaticamente. Em
# produção "tradicional" (Hostinger/Nginx, ver prod.py) isso continua
# desligado por padrão, pois o Nginx já cuida disso (ver nginx/nginx.conf).
# ---------------------------------------------------------------------------
SERVE_MEDIA = config("SERVE_MEDIA", default=False, cast=bool)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Cache — usado pelo app de métricas para deduplicar visitantes/visualizações
# e para cachear a agregação do dashboard por alguns minutos (ver
# apps/metrics). LocMemCache é suficiente para o volume de uma loja de porte
# pequeno/médio rodando num único processo lógico; se um dia for necessário
# múltiplos servidores ou dedupe perfeito entre workers, trocar por Redis
# aqui é a única mudança necessária.
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sandraellen-cache",
    }
}

# ---------------------------------------------------------------------------
# Sessão — logout automático por inatividade + rotação após login
# ---------------------------------------------------------------------------
SESSION_COOKIE_AGE = 60 * 60 * 2          # 2h de inatividade
SESSION_SAVE_EVERY_REQUEST = True          # renova o cookie a cada request ativo
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # precisa ser legível por JS só se usarmos CSRF via fetch; manter False é o padrão Django
CSRF_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------------
# Uploads — validação de tipo/tamanho (ver apps/catalog/validators.py)
# ---------------------------------------------------------------------------
MAX_UPLOAD_SIZE_MB = config("MAX_UPLOAD_SIZE_MB", default=5, cast=int)
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
ALLOWED_IMAGE_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# ---------------------------------------------------------------------------
# Rate limiting / brute-force no login (django-axes)
# ---------------------------------------------------------------------------
INSTALLED_APPS += ["axes"]
MIDDLEWARE.insert(2, "axes.middleware.AxesMiddleware")
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_RESET_ON_SUCCESS = True
# O Nginx do projeto é o único proxy entre o cliente e o Django (1 hop confiável).
# Sem isso, o axes pode confiar no X-Forwarded-For sem validar de onde ele veio,
# permitindo que um atacante forje o próprio IP e nunca seja bloqueado.
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_PROXY_ORDER = "left-most"

LOGIN_URL = "admin:login"

# ---------------------------------------------------------------------------
# WhatsApp / dados fixos usados nos templates de fallback
# ---------------------------------------------------------------------------
WHATSAPP_NUMBER = config("WHATSAPP_NUMBER", default="557532662033")

# ---------------------------------------------------------------------------
# Logging — login/logout/CRUD/erros/uploads (ver apps/core/signals.py)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "sandraellen.audit": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
    },
}

SITE_DOMAIN = config("SITE_DOMAIN", default="www.sandraellenmodas.com.br")
SITE_NAME = "Sandra Ellen Modas"
