# Guia de Deploy — Hostinger VPS KVM 1

Guia específico para colocar o site **Sandra Ellen Modas** no ar na sua VPS
Hostinger KVM 1 (1 vCPU, 4 GB RAM, 50 GB NVMe), usando o domínio
**sandraellenmodas.com**.

Já deixei prontos: `.env` (com `SECRET_KEY` e senha de banco geradas), `nginx/nginx.conf`
(com o domínio configurado) e `nginx/nginx-bootstrap.conf` (config temporária para emitir o
certificado SSL). Você só precisa seguir os passos abaixo.

---

## 0. Antes de começar

- Compre e finalize o registro do domínio `sandraellenmodas.com`.
- No painel da Hostinger, crie a VPS **KVM 1** com imagem **Ubuntu 22.04 (ou 24.04) com Docker**
  (a Hostinger tem um template pronto "Ubuntu + Docker" — escolha ele pra pular a instalação manual do Docker).
- Anote o **IP da VPS** (aparece no painel da Hostinger, em "Visão geral" da VPS).

---

## 1. Aponte o domínio para a VPS

No painel onde você comprou o domínio (ou no painel de DNS da Hostinger, se o domínio for
gerenciado por lá), crie estes dois registros:

| Tipo | Nome | Valor           |
|------|------|-----------------|
| A    | @    | `IP_DA_SUA_VPS` |
| A    | www  | `IP_DA_SUA_VPS` |

A propagação pode levar de alguns minutos até ~24h. Você pode conferir se já propagou rodando
`ping sandraellenmodas.com` no seu computador — se ele responder com o IP da VPS, já propagou.
**Só siga para o passo 5 (emitir SSL) depois de confirmar que propagou.**

---

## 2. Acesse a VPS via SSH

```bash
ssh root@IP_DA_SUA_VPS
```

Se o template não veio com Docker, instale:

```bash
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin
```

Confirme:
```bash
docker --version
docker compose version
```

## 3. Libere o firewall (portas 80 e 443)

```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

## 4. Envie o projeto pra VPS

Do seu computador (não da VPS), com o projeto já descompactado localmente:

```bash
scp -r "SITE SANDRA ELLEN MODAS" root@IP_DA_SUA_VPS:/root/sandraellen
```

Ou, se preferir usar Git, suba o projeto pra um repositório privado antes e depois:
```bash
git clone <seu-repositorio> /root/sandraellen
```
(nesse caso, lembre que o `.env` não vai junto pro Git — copie ele separadamente por `scp`
já que ele tem suas senhas reais.)

Depois, entre na pasta na VPS:
```bash
cd /root/sandraellen
```

## 5. Suba o banco e a aplicação (ainda sem HTTPS)

Primeiro usamos a config temporária do Nginx (sem SSL), porque o certificado ainda não existe:

```bash
cp nginx/nginx.conf nginx/nginx-ssl-final.conf.bak
cp nginx/nginx-bootstrap.conf nginx/nginx.conf

docker compose up -d db
docker compose up -d web
docker compose up -d nginx
```

Aguarde ~15s e teste: acesse `http://sandraellenmodas.com` no navegador. O site deve carregar
normalmente em HTTP (sem cadeado ainda — é esperado nessa etapa).

Se der erro, veja os logs:
```bash
docker compose logs web --tail=50
docker compose logs nginx --tail=50
```

## 6. Emita o certificado SSL (Let's Encrypt)

```bash
docker compose run --rm certbot certonly --webroot -w /var/www/certbot \
  -d sandraellenmodas.com -d www.sandraellenmodas.com \
  --email pedromota07@hotmail.com --agree-tos --non-interactive
```

Se aparecer "Congratulations! Your certificate and chain have been saved", deu certo.

## 7. Ative a config definitiva (com HTTPS)

```bash
cp nginx/nginx-ssl-final.conf.bak nginx/nginx.conf
docker compose up -d
```

Isso sobe tudo (incluindo o serviço `certbot` que renova o certificado sozinho a cada 12h,
e o `db-backup` que faz backup diário do banco). Acesse agora `https://sandraellenmodas.com` —
já deve aparecer o cadeado.

## 8. Crie o usuário administrador do painel

Os usuários `pedro` e `ellen` (com os produtos, categorias e marcas já cadastrados) vêm
prontos no arquivo `fixtures/dados_iniciais.json` — importe-os assim, **em vez de** criar
um superusuário do zero:

```bash
docker compose exec web python manage.py loaddata fixtures/dados_iniciais.json
```

Isso recria no Postgres exatamente os produtos, categorias, marcas, informações da loja e
os 2 logins de administrador que já existiam no ambiente de testes. As senhas continuam as
mesmas que você já usa hoje para entrar no `/admin/`.

As fotos dos produtos (pasta `media/`) não precisam de nenhum passo extra: o Docker já
copia esses arquivos pra dentro do volume de mídia automaticamente na primeira subida do
container, porque a pasta já vem com as imagens reais dentro do pacote.

Se preferir começar do zero (sem os dados de teste) em vez de importar o fixture, crie um
superusuário novo normalmente:
```bash
docker compose exec web python manage.py createsuperuser
```

Depois de qualquer uma das duas opções, acesse `https://sandraellenmodas.com/admin/`.

## 9. Confirme que está tudo de pé

```bash
docker compose ps
```

Todos os serviços (`db`, `web`, `nginx`, `certbot`, `db-backup`) devem aparecer como `Up`.

---

## Comandos úteis no dia a dia

| O que você quer fazer                  | Comando                                                   |
|-----------------------------------------|------------------------------------------------------------|
| Ver logs da aplicação                   | `docker compose logs web -f`                                |
| Reiniciar tudo                          | `docker compose restart`                                    |
| Atualizar o código (depois de mudanças) | `docker compose up -d --build web`                           |
| Rodar um comando Django                 | `docker compose exec web python manage.py <comando>`        |
| Backup manual do banco                  | `docker compose exec db pg_dump -U sandraellen sandraellen > backup.sql` |
| Ver uso de recursos (CPU/RAM)           | `docker stats`                                               |

## Sobre os recursos da KVM 1 (1 vCPU / 4 GB RAM)

O `entrypoint.sh` já sobe o Gunicorn com 3 workers, que é o recomendado para 1 vCPU
(fórmula `2×núcleos + 1`). Com Postgres + Nginx + Django rodando junto, o consumo de RAM
em operação normal fica bem dentro dos 4 GB — não precisa mexer em nada. Se no futuro o
catálogo crescer muito e o site começar a ficar lento, o primeiro passo é fazer upgrade
de plano (mais vCPU/RAM) antes de otimizar código.

## Checklist final antes de divulgar o site

- [ ] `https://sandraellenmodas.com` carrega com cadeado (SSL ok)
- [ ] `https://www.sandraellenmodas.com` também funciona
- [ ] Painel `/admin/` acessível e você já trocou a senha do superusuário
- [ ] Produtos de teste substituídos pelos produtos reais
- [ ] Número de WhatsApp no `.env` (`WHATSAPP_NUMBER`) conferido
- [ ] Backup automático rodando (`docker compose logs db-backup`)
