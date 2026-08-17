# Sandra Ellen Modas — Sistema de Catálogo

Catálogo digital de moda feminina com painel administrativo completo. Sem pagamento online —
todo contato de venda é redirecionado para o WhatsApp.

Stack: **Django 5 + PostgreSQL + Gunicorn + Nginx**, containerizado com **Docker**.

---

## 1. Rodando localmente (sem Docker, pra desenvolver)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # edite e coloque DEBUG=True, DJANGO_SETTINGS_MODULE=config.settings.dev

python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://localhost:8000` (site) e `http://localhost:8000/admin/` (painel).

Em modo dev, o banco é SQLite automaticamente (não precisa instalar Postgres local).

---

## 2. Deploy em produção (VPS com Docker)

### Pré-requisitos na VPS
- Docker e Docker Compose instalados
- Domínio apontando (registro A) para o IP da VPS
- Portas 80 e 443 liberadas no firewall

### Passos

```bash
# 1. Envie o projeto para a VPS (git clone ou scp)
git clone <seu-repositorio> sandraellen && cd sandraellen

# 2. Configure o ambiente
cp .env.example .env
nano .env   # preencha SECRET_KEY, ALLOWED_HOSTS, senha do banco, etc.

# 3. Ajuste o domínio no Nginx
nano nginx/nginx.conf   # troque "SEU_DOMINIO_AQUI" pelo domínio real (2 ocorrências + certificado)

# 4. Suba o banco e o Nginx primeiro (sem SSL ainda) para emitir o certificado
docker compose up -d db
docker compose up -d web

# 5. Emita o certificado Let's Encrypt (primeira vez)
docker compose run --rm certbot certonly --webroot -w /var/www/certbot \
  -d seudominio.com.br -d www.seudominio.com.br --email voce@email.com --agree-tos

# 6. Suba tudo
docker compose up -d

# 7. Crie o superusuário do painel
docker compose exec web python manage.py createsuperuser
```

O `entrypoint.sh` já roda migrations, `collectstatic` e cria os grupos de permissão
automaticamente toda vez que o container `web` sobe.

### Renovação do certificado SSL
O serviço `certbot` no `docker-compose.yml` já roda em loop renovando automaticamente
a cada 12h (renova só quando está perto de expirar).

### Backup automático do banco
O serviço `db-backup` gera um dump `.sql.gz` por dia em `./backups/`, mantendo os últimos 14 dias.
Para restaurar: `gunzip -c backups/backup_XXX.sql.gz | docker compose exec -T db psql -U <DB_USER> <DB_NAME>`.

---

## 3. Estrutura do projeto

```
config/            → settings (base/dev/prod), urls, wsgi
apps/core/          → dados institucionais da loja, banners, horários, auditoria, segurança
apps/catalog/        → produtos, categorias, marcas, catálogo público, SEO (sitemap)
apps/pages/          → páginas legais (LGPD): privacidade, cookies, termos
apps/accounts/       → grupos de permissão (Administrador/Editor/Funcionário)
apps/metrics/        → painel de métricas (visitantes, produtos vistos, cliques no WhatsApp)
templates/           → HTML (mantém a identidade visual preto/dourado original)
static/              → CSS/JS extraídos e adaptados da landing page original
nginx/               → configuração do proxy reverso
```

## 4. Papéis de usuário

Rode `python manage.py setup_groups` para criar os 3 grupos:
- **Administrador**: acesso total
- **Editor**: gerencia produtos, categorias, marcas, banners e conteúdo institucional
- **Funcionário**: só visualiza e atualiza produtos (sem excluir)

Crie os usuários da equipe pelo próprio admin (`/admin/auth/user/add/`) e associe ao grupo adequado.

## 5. Painel de Métricas

Acesse **Admin → Métricas** (`/admin/metricas/`) para ver, sem depender de Google Analytics
ou qualquer ferramenta externa:

- Visitantes (total, hoje, 7 dias, 30 dias, média diária) e gráfico por dia
- Produtos mais visualizados (Top 10) e gráfico
- Cliques no botão do WhatsApp (total, por produto, por dia)

Tudo é coletado internamente (middleware + banco de dados), com deduplicação para não contar
o mesmo visitante várias vezes em poucos segundos, e o IP é gravado de forma anonimizada
(último octeto zerado). O dashboard é cacheado por 2 minutos para não pesar no banco em caso
de atualizações frequentes da página.

## 6. O que ainda vale reforçar antes de ir ao ar de vez

Este projeto já sai do zero com toda a base de segurança, SEO e LGPD pedida, testada e funcionando
(migrations rodaram, páginas renderizam, upload comprime imagem, login com Argon2, admin operacional).
Ainda assim, antes de um lançamento real recomendo:

- Rodar `python manage.py check --deploy` no ambiente de produção real e revisar os avisos
- Testar Lighthouse/Core Web Vitals com imagens reais dos produtos (o peso final depende do conteúdo)
- Configurar um provedor de e-mail (SMTP) se quiser notificações de erro por e-mail
- Revisar a política de privacidade/cookies com um advogado antes de publicar, se possível
- Trocar a senha do superusuário de teste e o `SECRET_KEY` de exemplo antes de ir para produção
