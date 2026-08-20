"""
Configurações específicas para deploy na Vercel — Sandra Ellen Modas.

Estende config/settings/prod.py (que já cuida de DEBUG=False, HTTPS,
HSTS etc.) e ajusta somente o que é necessário por causa do ambiente
serverless da Vercel:

  0. SECRET_KEY: base.py exige a variável SECRET_KEY (python-decouple,
     sem default). Aqui aplicamos um fallback SEGURO apenas para não
     quebrar o build/demo caso a variável ainda não tenha sido cadastrada
     no painel da Vercel. Assim que SECRET_KEY for definida nas
     Environment Variables da Vercel, ela tem prioridade sobre o
     fallback automaticamente.
  1. Domínio *.vercel.app: a Vercel injeta a variável VERCEL_URL em todo
     deploy (produção e preview). Além de adicionar VERCEL_URL, também
     liberamos o domínio coringa ".vercel.app" em ALLOWED_HOSTS e
     "https://*.vercel.app" em CSRF_TRUSTED_ORIGINS, para cobrir
     qualquer preview sem precisar cadastrar host por host.
  2. Banco de dados — DEMONSTRAÇÃO com SQLite: nesta etapa o objetivo é
     mostrar o catálogo já cadastrado ao cliente, então o banco padrão
     nesta configuração é o db.sqlite3 já existente no projeto (versionado
     no Git, ver .gitignore), localizado via BASE_DIR. Se no futuro uma
     variável DATABASE_URL (Postgres/Neon/Supabase) for configurada na
     Vercel, ela passa a ter prioridade automaticamente — não é preciso
     alterar este arquivo para migrar depois.
  3. Mídia: SERVE_MEDIA = True, para que o próprio Django sirva as imagens
     de /media/ (ver base.py e config/urls.py), já que não há Nginx na
     frente do Django nesse ambiente serverless.
  4. Logging em arquivo: o filesystem da Vercel é somente leitura em
     runtime (exceto /tmp). O RotatingFileHandler de base.py, que grava
     em logs/app.log, quebraria a aplicação. Aqui usamos apenas o
     handler de console — a Vercel já captura stdout/stderr como logs
     da função.

Nada de design, template, view ou regra de negócio é alterado aqui —
só configuração de ambiente.
"""
import os
import urllib.parse

# ---------------------------------------------------------------------------
# 0) Fallback de SECRET_KEY só para não travar o build de demonstração.
#    IMPORTANTE: cadastre a variável SECRET_KEY nas Environment Variables
#    da Vercel com um valor real antes de divulgar a URL para o cliente.
#    os.environ.setdefault não sobrescreve um valor já definido lá.
# ---------------------------------------------------------------------------
os.environ.setdefault(
    "SECRET_KEY",
    "django-insecure-demo-sandra-ellen-modas-TROQUE-NAS-ENV-VARS-DA-VERCEL",
)

from .prod import *  # noqa

# ---------------------------------------------------------------------------
# 1) Domínio da Vercel
# ---------------------------------------------------------------------------
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL and VERCEL_URL not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, VERCEL_URL]
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, f"https://{VERCEL_URL}"]

if ".vercel.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, ".vercel.app"]
if "https://*.vercel.app" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, "https://*.vercel.app"]

# ---------------------------------------------------------------------------
# 2) Banco de dados — SQLite por padrão nesta demonstração (ver docstring)
# ---------------------------------------------------------------------------
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}

# Se uma integração de Postgres (Neon/Supabase/etc.) for conectada na Vercel
# e fornecer DATABASE_URL, ela assume automaticamente no lugar do SQLite.
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
# 3) Mídia — Django serve /media/ diretamente (sem Nginx nesse ambiente)
# ---------------------------------------------------------------------------
SERVE_MEDIA = True

# ---------------------------------------------------------------------------
# 4) Logging apenas em console (sem escrita em disco)
# ---------------------------------------------------------------------------
LOGGING["root"]["handlers"] = ["console"]
for _logger_cfg in LOGGING["loggers"].values():
    _logger_cfg["handlers"] = ["console"]
