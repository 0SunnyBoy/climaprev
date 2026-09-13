# Arquitetura do Clima Prev

**Estado:** implementação observada em 2026-09-13, com evolução indicada
separadamente. [Índice](../PROJECT.md).

## Visão de contexto

```mermaid
flowchart LR
    Cliente["Cliente HTTP"] -->|"GET /api/v1/risk"| API["Clima Prev - FastAPI"]
    API -->|"JSON: previsão, risco e qualidade"| Cliente
    API <-->|"Cache, lock e rate limit"| Redis[(Redis)]
    API -->|"Texto do local"| Geo["Open-Meteo Geocoding"]
    Geo -->|"Local e coordenadas"| API
    API -->|"Coordenadas, datas e variáveis"| Meteo["Open-Meteo Forecast"]
    Meteo -->|"Séries diárias e horárias"| API
    API --> Logs["Logs e contadores em memória"]
```

Não há frontend, banco relacional, fila de mensagens ou serviço externo de
alertas oficiais configurado no código atual.

## Componentes e responsabilidades

| Camada               | Evidência                                                                                                                                                                                              | Responsabilidade e limite                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Entrada HTTP         | [Rotas](../src/climaprev/api/routes/risk.py), [schema](../src/climaprev/api/schemas/risk.py)                                                                                                           | Validar query e serializar resposta; não calcular risco.          |
| Proteção de entrada  | [Dependências](../src/climaprev/api/deps.py)                                                                                                                                                           | Resolver identidade de rede e aplicar rate limit.                 |
| Aplicação            | [Serviço de consulta](../src/climaprev/application/services/forecast_query.py)                                                                                                                         | Resolver local, cache, lock, previsão, avaliação e alertas.       |
| Contratos internos   | [Portas](../src/climaprev/application/ports.py), [query](../src/climaprev/application/query.py)                                                                                                        | Separar operações de suas implementações.                         |
| Domínio              | [Modelos](../src/climaprev/domain/models.py), [avaliador](../src/climaprev/domain/risk_evaluator.py), [política](../src/climaprev/domain/risk_policy.py)                                               | Regras determinísticas sem acesso à rede.                         |
| Meteorologia         | [Adaptador](../src/climaprev/infrastructure/providers/open_meteo.py), [HTTP](../src/climaprev/infrastructure/http/client.py)                                                                           | Consultar e normalizar respostas externas.                        |
| Estado compartilhado | [Cache](../src/climaprev/infrastructure/cache/redis_cache.py), [lock](../src/climaprev/infrastructure/cache/redis_lock.py), [limite](../src/climaprev/infrastructure/rate_limit/redis_rate_limiter.py) | Redis para estado temporário; não fornece histórico de consultas. |
| Composição           | [main.py](../src/climaprev/main.py), [configuração](../src/climaprev/config.py)                                                                                                                        | Criar clientes e injetar dependências no ciclo de vida do app.    |

```mermaid
flowchart TB
    HTTP["API e schemas"] --> App["ForecastQueryService"]
    App --> Domain["RiskEvaluator e RiskPolicy"]
    App --> Ports["Portas de aplicação"]
    Adapters["Adaptadores Open-Meteo e Redis"] -.->|"Implementam"| Ports
    Main["main.py - composição"] --> HTTP
    Main --> App
    Main --> Adapters
```

O desenho segue camadas e portas, mas a separação não é absoluta:
`ForecastQueryService` importa `ProviderTransientError` de infraestrutura.
Uma evolução pode mover a exceção para o contrato de aplicação. Isso é uma
lacuna de dependência, não uma extração de serviço já realizada.

## Implantação existente

- Python `>=3.12,<3.13`, FastAPI, Uvicorn, HTTPX e Redis, declarados no
  [pyproject.toml](../pyproject.toml).
- O [Compose](../docker-compose.yml) publica a API em
  `127.0.0.1:8000`; Redis não publica porta para o host.
- A rede `local` é uma rede Compose comum. Seu nome não bloqueia acesso à
  internet; a aplicação padrão consulta Open-Meteo externo.
- O [Dockerfile](../Dockerfile) inicia Uvicorn com `--no-proxy-headers`.
  A API tem sua própria interpretação controlada de `X-Forwarded-For`.
- O processo mantém clientes HTTP/Redis no lifespan e os fecha na saída.
- Réplicas podem compartilhar Redis; métricas em memória permanecem separadas
  por processo. O perfil `app-load` usa dois workers.
- Não há volume persistente declarado para Redis, TLS de entrada, proxy de
  produção ou exportador de métricas no Compose atual.

## Perfil de carga

`load` executa Locust contra `app-load`, com `provider-mock` interno e Redis
real. `app-load` usa ambiente `load` e limites elevados explícitos. As chaves
têm namespace por ambiente, mas app e carga compartilham o mesmo serviço Redis
no Compose; portanto, ainda disputam seus recursos.

O mock de carga não comprova desempenho nem disponibilidade do Open-Meteo
público. Consulte [operações](operations.md) para os comandos existentes.

## Evolução proposta

```mermaid
flowchart LR
    UI["Frontend futuro"] --> Edge["Entrada HTTPS e controle de tráfego"]
    Edge --> API["API Clima Prev"]
    API --> Redis[("Redis com isolamento operacional")]
    API --> Provider["Provedor meteorológico"]
    API -.-> Alerts["Integração futura de alertas oficiais"]
    API --> Obs["Coleta externa de logs e métricas"]
```

Todo o diagrama acima é um alvo de implantação, não uma descrição de serviços
já entregues. Manter a avaliação no backend, usar somente contratos públicos
no frontend e decidir autenticação antes de introduzir dados privados. Não há
necessidade demonstrada de transformar as camadas em microserviços agora.
