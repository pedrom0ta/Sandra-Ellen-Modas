"""
Constantes e helpers de baixo nível do app de métricas.
"""

# Janela de dedupe de visitantes: acessos consecutivos da mesma sessão dentro
# desse intervalo NÃO geram uma nova linha em Visit (evita contar refresh,
# navegação entre páginas ou o carregamento de assets como visitas novas).
# 30 minutos é a mesma convenção usada por ferramentas de web analytics para
# definir o que é "uma sessão".
VISIT_DEDUPE_SECONDS = 60 * 30

# Janela de dedupe de visualização de produto: um pouco menor, porque faz
# sentido registrar de novo se o visitante voltar à mesma peça depois de um
# tempo (ex: comparando produtos), mas não a cada F5.
PRODUCT_VIEW_DEDUPE_SECONDS = 60 * 10

# Nota sobre cache multi-processo: o cache padrão do projeto (LocMemCache) é
# local a cada worker do Gunicorn. Com 3 workers, na pior das hipóteses um
# mesmo visitante pode gerar até 3 linhas em vez de 1 dentro da mesma janela,
# se cada request cair num worker diferente. Isso é uma imprecisão aceitável
# para um painel de métricas (não é billing nem dado sensível); se o tráfego
# crescer muito, trocar CACHES para Redis resolve isso sem mudar mais nada
# aqui.


def visit_cache_key(session_key: str) -> str:
    return f"metrics:visit:{session_key}"


def product_view_cache_key(session_or_ip: str, product_id: int) -> str:
    return f"metrics:pview:{session_or_ip}:{product_id}"
