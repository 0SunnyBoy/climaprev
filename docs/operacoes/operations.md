# Operação do ClimaPrev

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.
>
> Operação atual: origem pública da API configurada no build do frontend, Composes próprios e modo integrado mantido; prazo cooperativo padrão de consulta 7 s. INMET real e CI remota da revisão local pendentes. Hospedagem/publicação adiada; templates de monitoramento não provisionados.

## Configuração e saúde

As variáveis usam o prefixo `CLIMAPREV_`: `REDIS_URL` (também aceito por
compatibilidade), `CLIMAPREV_ENVIRONMENT`, `CLIMAPREV_RATE_LIMIT`,
`CLIMAPREV_RATE_LIMIT_BURST`, `CLIMAPREV_RATE_LIMIT_WINDOW_SECONDS`,
`CLIMAPREV_CORS_ALLOW_ORIGINS`, `CLIMAPREV_TRUSTED_PROXY_IPS`, URLs Open-Meteo
e INMET, timeouts, limites de conexão e `CLIMAPREV_ADDITIONAL_RETRIES` (máximo
dois). Redis é estado
compartilhado para cache, lock e rate limit; execute réplicas sem afinidade e
use Redis gerenciado com alta disponibilidade em produção.

`GET /health/live` não depende de Redis. `GET /health/ready` exige Redis e
deve ser o health check de tráfego. Cada resposta carrega `X-Request-ID`;
propague-o em incidentes.

No desenvolvimento, acesse a interface em `http://localhost:8080`. O serviço
`app` fica disponível em `http://localhost:8000` somente para acesso direto à
API e debug. Em homologação, a entrada TLS serve o frontend e encaminha API e
health check; API e Redis não publicam portas diretas.

## Integração contínua

O workflow [CI](../../.github/workflows/ci.yml) executa em cada `push`, Pull
Request ou acionamento manual. A revisão local valida Composes integrado/API-only/frontend-only, builds separados, lint/Vitest/auditoria Node, pytest, Ruff/mypy, isolamento do runtime, Nginx/HTTP e gate HTTPS entre origens distintas. O GitHub ainda usa o workflow anterior até o envio dos commits revisados; aprovação remota antiga não valida o diff local. A CI valida o código em um runner temporário e não faz
deploy.

## Observabilidade e privacidade

Os logs JSON contêm rota, status, latência, cache, provider, retries,
`error_code` e request ID. Não inclua `location_text`, payload Open-Meteo,
tokens ou IP bruto em logs. O coletor expõe contadores de HTTP, cache,
upstream, retries, rate-limit, avaliação de risco, campos ausentes e estado de
dependência; conecte-o ao exporter corporativo antes de produção. IP é usado
somente para rate limit; proxies confiáveis devem ser configurados exatamente.

## Falhas e rollout

Em falha transitória do Open-Meteo, a API usa apenas entrada stale dentro de 15
minutos; sem dado válido retorna 503. Alertas oficiais são uma porta isolada:
o app consulta o INMET, retorna `available` quando obtém resposta válida e
`unavailable` quando a dependência falha. O risco heurístico não é alterado
pelos alertas.

A policy de risco é versionada (`reference-v1`). Faça rollout por canário,
monitore mudanças de distribuição de `forecast_risk`, e faça rollback para a
versão anterior sem alterar entradas meteorológicas. Portas, DTO `ForecastQuery`
e adaptadores mantêm fronteiras para futura extração em microserviços (provider,
política e alertas oficiais).

## Carga

O Locust aceita `CLIMAPREV_LOAD_SCENARIO=warm_cache|cold_cache|lock_contention|slow_upstream|redis_latency`.
Essas configurações existem somente no perfil Compose `load`; o serviço `app`
padrão não recebe nenhuma delas. `warm_cache` prima e repete uma chave fixa;
`cold_cache` gera uma `location_text` única por requisição; `slow_upstream`
injeta atraso no provider mock por `CLIMAPREV_PROVIDER_MOCK_DELAY_MS` (150 ms
por padrão); e `redis_latency` injeta atraso em cada operação Redis do
`app-load` por `CLIMAPREV_LOAD_REDIS_OPERATION_DELAY_MS` (50 ms por padrão).
Os dois atrasos são configuráveis sem tocar o serviço padrão.

O Locust usa `constant_throughput`: cada usuário tem taxa de chegada de 1
requisição/s por padrão, ajustável por
`CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER`. Assim, 100 usuários devem
produzir 100 req/s com tolerância de ±10% (90--110 req/s), após o aquecimento.
Taxa fora dessa faixa invalida o baseline; 429 e 5xx são falhas distintas e
nunca contam como sucesso.

Além dos quatro cenários principais, `lock_contention` reutiliza uma chave
única entre usuários concorrentes para medir contenção do lock distribuído.

Smoke curto:

```bash
docker compose --profile load build load provider-mock app-load
docker compose --profile load up -d --wait provider-mock app-load
docker compose --profile load run --rm --no-deps load locust -f tests/load/locustfile.py --host http://app-load:8000 --headless --users 2 --spawn-rate 2 --run-time 10s --only-summary
```

O perfil `load` não usa a internet: `app-load` é a mesma aplicação FastAPI,
com Redis real e limite explícito de `100000` por minuto/burst, mas recebe URLs
de um `provider-mock` compatível com Open-Meteo. Ele existe apenas para carga;
`app` permanece configurado para Open-Meteo público. O resumo do Locust informa
throughput, p50, p95, p99 e falhas/5xx; 429 continua sendo falha de cenário.

Baseline proposto, apenas em ambiente dedicado:

```bash
export CLIMAPREV_LOAD_SCENARIO=warm_cache
export CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER=1
export CLIMAPREV_LOAD_RATE_LIMIT=100000
export CLIMAPREV_LOAD_RATE_LIMIT_BURST=100000
docker compose --profile load build load provider-mock app-load
docker compose --profile load up -d --wait provider-mock app-load
docker compose --profile load run --rm --no-deps load locust -f tests/load/locustfile.py --host http://app-load:8000 --headless --users 100 --spawn-rate 100 --run-time 10m --only-summary
```

Registre p50/p95/p99, throughput, 5xx e 429. Não trate 429 como capacidade:
100 req/s por 600 s precisa de limite compatível e identidades de carga
compatíveis. Registre também a faixa de 90--110 req/s e declare falha se ela
não for atingida.

## Atualizar dependências reproduzíveis

A plataforma validada é Python3.12 em Linuxamd64. `requirements.lock` registra
produção e transitivas; `requirements-build.lock` fixa ferramentas usadas
para construir o pacote sem resolução implícita em build isolation.

```bash
uv --no-config pip compile pyproject.toml --generate-hashes --no-header --python-version 3.12 --python-platform x86_64-unknown-linux-gnu --default-index https://pypi.org/simple -o requirements.lock
uv --no-config pip compile docker/build-requirements.in --generate-hashes --no-header --python-version 3.12 --python-platform x86_64-unknown-linux-gnu --default-index https://pypi.org/simple -o requirements-build.lock
docker compose build
docker compose run --rm app python tests/docker/check_lock_install.py
docker compose run --rm app pytest -q -W error
```

Executar resolução em ambiente sem variáveis de índices/credenciais pessoais.
Revisar o diff dos locks e executar Full/Ruff/mypy antes do commit da atualização.
A verificação explícita instala duas vezes em ambientes vazios, exige hashes,
executa pip check e compara todas as versões instaladas com o lock.

## Imagens de desenvolvimento e runtime

`docker compose build` seleciona `dev` explicitamente nos quatro serviços de
aplicação/carga. O alvo final padrão é `runtime`, com UID10001, dependências
hashadas e o wheel do pacote; testes/docs/env e ferramentas dev ficam fora.
O Python base está fixado por digest. O código HTML/CSS/TypeScript fica em
`frontend/`, é compilado pelo Vite e servido pelo Nginx a partir de `dist/`;
não entram no wheel nem na imagem de runtime Python. O `.dockerignore` envia
os arquivos necessários aos builds do backend e do frontend.

```bash
docker build --load --target runtime -t climaprev-runtime:local .
docker run --rm -v "$PWD/tests/docker/check_runtime_image.py:/check.py:ro" climaprev-runtime:local python /check.py
```


O perfil `app-load` conserva o token bucket global, com fixture de capacidade
e reposição 100000 por 60 s, exclusiva do provider mock. Os overrides são
`CLIMAPREV_LOAD_PROVIDER_BUDGET_CAPACITY`, `CLIMAPREV_LOAD_PROVIDER_BUDGET_REFILL`
e `CLIMAPREV_LOAD_PROVIDER_BUDGET_WINDOW_SECONDS`. Essa configuração não muda
a cota do app público. Separar recusas 503 por orçamento de medições de
processamento; não interpretar o limite como capacidade do Open-Meteo.


### Métricas e validação local — 20/10/2026

Exporter privado `/internal/metrics/prometheus`, habilitado por `CLIMAPREV_METRICS_AGGREGATION_ENABLED` (false por padrão), com snapshots por worker em Redis a cada 5 s e lease de 20 s. Leitura limitada a 256 workers e 2 s; incompletude/indisponibilidade retorna 503. Nginx bloqueia acesso público a `/internal/`. Usar taxas por worker e histogramas cumulativos agregados, sem médias de percentis. Atualizar ACLs existentes de forma controlada para ZADD/ZRANGE/ZREMRANGEBYSCORE no namespace antes da habilitação; o provisionador atualizado não altera credenciais antigas automaticamente. Templates em `monitoramento/` ainda não são serviços instalados; retenção proposta de 30 dias exige armazenamento externo próprio. Destinos e limiares precisam de validação operacional futura.

Prazo global do serviço público: padrão 7 s, máximo configurável 8 s, cancelamento cooperativo com cleanup; cliente aguarda 10 s. Transporte/parsing/rate limit anteriores ao serviço não estão incluídos. Carga local limitada: 3.000 requisições sem falhas em cinco cenários, não benchmark da futura hospedagem. Ver relatório `execucao-frentes-1-a-7-2026-10-20.md`. Hospedagem adiada por orientação do usuário.
