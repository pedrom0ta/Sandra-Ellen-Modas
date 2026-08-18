"""
Configurações específicas para deploy na Vercel — Sandra Ellen Modas.

Estende config/settings/prod.py (que já cuida de DEBUG=False, HTTPS,
HSTS etc.) e ajusta somente o que é necessário por causa do ambiente
serverless da Vercel:

  1. Domínio *.vercel.app: a Vercel injeta a variável VERCEL_URL em todo
     deploy (produção e preview). Adicionamos automaticamente a
     ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS para não precisar cadastrar cada
     URL de preview manualmente.
  2. DATABASE_URL: quando a Vercel (ou uma integração de Postgres tipo
     Neon/Supabase) fornece essa variável no formato de connection
     string, usamos ela. Se não existir, mantém o comportamento já
     herdado de base.py (DB_NAME/DB_USER/DB_HOST/...).
  3. Logging em arquivo: o filesystem da Vercel é somente leitura em
     runtime (exceto /tmp). O RotatingFileHandler de base.py, que grava
     em logs/app.log, quebraria a aplicação. Aqui usamos apenas o
     handler de console — a Vercel já captura stdout/stderr como logs
     da função.

Nada de design, template, view ou regra de negócio é alterado aqui —
só configuração de ambiente.
"""
import os
import urllib.parse

from .prod import *  # noqa

# ---------------------------------------------------------------------------
# 1) Domínio da Vercel
# ---------------------------------------------------------------------------
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL and VERCEL_URL not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, VERCEL_URL]
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, f"https://{VERCEL_URL}"]

# ---------------------------------------------------------------------------
# 2) Banco de dados via DATABASE_URL (quando disponível)
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    _parsed = urllib.parse.urlparse(DATABASE_URL)
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _parsed.path.lstrip("/"),
        "USER": _parsed.username,
        "PASSWORD": _parsed.password,
        "HOST": _parsed.hostname,
        "PORT": _parsed.port or 5432,
        "CONN_MAX_AGE": 60,
    }

# ---------------------------------------------------------------------------
# 3) Logging apenas em console (sem escrita em disco)
# ---------------------------------------------------------------------------
LOGGING["root"]["handlers"] = ["console"]
for _logger_cfg in LOGGING["loggers"].values():
    _logger_cfg["handlers"] = ["console"]
