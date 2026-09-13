# Fluxos de consulta e operação

**Estado:** comportamento atual, salvo a jornada identificada como proposta.
[Índice](../PROJECT.md).

## Consulta principal

1. O middleware valida ou gera `request_id`.
2. A rota executa dependências de limite por cliente e validação da query.
   Uma rejeição de limite pode ocorrer antes de a entrada ser validada.
3. Com texto, o serviço consulta cache de geocodificação e, se necessário,
   Open-Meteo Geocoding. Com coordenadas, constrói o local diretamente.
4. O serviço consulta previsão normalizada no Redis, usando local e datas.
5. Em cache fresco, usa o dado. Caso contrário, disputa o lock de atualização.
6. O detentor do lock verifica o cache novamente, consulta o provedor,
   normaliza os dados e grava o resultado. Renova o lock durante a consulta.
7. O domínio calcula risco em Celsius, milímetros e km/h.
8. O serviço obtém o estado de alertas oficiais e converte temperaturas de
   saída se o cliente pediu Fahrenheit.
9. A API responde com previsão, risco, qualidade, fonte, aviso e `request_id`.
   O middleware registra metadados da requisição.

Evidências: [rota](../src/climaprev/api/routes/risk.py),
[serviço](../src/climaprev/application/services/forecast_query.py) e
[middleware](../src/climaprev/api/observability.py).

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API
    participant S as Serviço de consulta
    participant R as Redis
    participant G as Geocoding
    participant P as Forecast
    participant D as Domínio
    C->>A: GET /api/v1/risk
    A->>R: Rate limit por identidade de rede
    A->>S: Query validada e request_id
    opt Local informado por texto
        S->>R: Consultar cache de local
        opt Cache de local ausente
            S->>G: name e language=pt
            G-->>S: Local canônico
            S->>R: Armazenar por 24 horas
        end
    end
    S->>R: Consultar cache de previsão
    alt Previsão fresca
        R-->>S: Previsão normalizada
    else Atualização necessária e lock obtido
        S->>R: Lock e nova consulta ao cache
        S->>P: Coordenadas, datas e variáveis
        P-->>S: Séries meteorológicas
        S->>R: Gravar previsão e liberar lock
    end
    S->>D: Avaliar com reference-v1
    D-->>S: Nível e condições
    Note over S: Alertas atuais: not_configured
    S-->>A: Resultado e temperaturas de saída
    A-->>C: JSON com qualidade e fonte
```

## Cache e concorrência

| Estado                               | Ação atual                                    | Resultado                                   |
| ------------------------------------ | --------------------------------------------- | ------------------------------------------- |
| Previsão com idade menor que 10 min  | Usar cache.                                   | `hit`, `is_stale=false`.                    |
| Previsão entre 10 e 15 min           | Tentar atualização.                           | Resultado novo ou fallback permitido.       |
| Sem previsão ou com 15 min completos | Tentar atualização.                           | Não há fallback válido dessa entrada.       |
| Outro worker detém o lock            | Consultar lock/cache a cada 10 ms, até 30 s.  | Usar cache fresco que surgir ou obter lock. |
| Espera de lock encerrada             | Revalidar a expiração do stale antes de usar. | `stale` ou 503.                             |
| Atualização bem-sucedida             | Salvar previsão com TTL total de 15 min.      | `miss`, `is_stale=false`.                   |
| Falha transitória do forecast        | Revalidar a expiração do stale antes de usar. | `stale` ou 503.                             |

O lock dura 10 s e recebe renovação a cada 5 s, com token de propriedade.
A geocodificação não usa esse lock; textos distintos podem gerar consultas
externas concorrentes.

A validade do stale é reavaliada após espera, retries e consulta opcional de
alertas, imediatamente antes da entrega. Em 900 segundos completos, a entrada
não pode ser usada. Leituras não renovam seu TTL. Corrupção do envelope de
cache produz miss e um contador fixo; indisponibilidade do Redis produz 503.
Perda de propriedade do lock cancela e aguarda a consulta externa, impede a
gravação e retorna 503, sem fallback. A liberação só remove o token próprio;
falha de limpeza não substitui um erro principal já identificado.

## Falhas e resposta ao consumidor

| HTTP / código                        | Significado                                                | Tratamento esperado no futuro cliente           |
| ------------------------------------ | ---------------------------------------------------------- | ----------------------------------------------- |
| 422 / `INVALID_LOCATION_INPUT`       | Local ausente, conflitante ou inválido.                    | Corrigir entrada.                               |
| 422 / `INVALID_PERIOD`               | Data inválida, ordem incorreta ou mais de sete dias.       | Corrigir período.                               |
| 422 / `INVALID_TEMPERATURE_UNIT`     | Unidade não aceita.                                        | Selecionar unidade contratada.                  |
| 404 / `LOCATION_NOT_FOUND`           | Geocodificação sem local utilizável.                       | Refinar busca.                                  |
| 429 / `RATE_LIMIT_EXCEEDED`          | Limite excedido.                                           | Respeitar `Retry-After`.                        |
| 502 / `WEATHER_DATA_INVALID`         | Estrutura meteorológica inválida.                          | Exibir indisponibilidade dos dados.             |
| 502 / `WEATHER_PROVIDER_REJECTED`    | Provedor rejeitou a consulta com 4xx diferente de 429.     | Exibir falha da consulta, sem retry automático. |
| 503 / `WEATHER_PROVIDER_UNAVAILABLE` | Falha transitória sem fallback ou espera de lock sem dado. | Permitir nova tentativa com espera.             |
| 503 / `DEPENDENCY_UNAVAILABLE`       | Redis indisponível.                                        | Exibir indisponibilidade do serviço.            |
| 500 / `INTERNAL_ERROR`               | Falha não mapeada.                                         | Mostrar erro e identificador de suporte.        |

Os [handlers](../src/climaprev/main.py) usam mensagens sanitizadas. Um 429 do
provedor produz 503, sem retry; forecast pode usar stale ainda válido. Outros
4xx produzem 502, sem retry nem fallback. Timeout, rede e 5xx permitem até
três tentativas. Dado meteorológico inválido não aciona retry nem stale.
O 429 público permanece reservado ao limite individual do cliente.

O provedor opcional de alertas, quando implementado, pode falhar sem bloquear a
previsão: o serviço retorna `official_alerts.status=unavailable`. Atualmente
o provedor instalado sempre indica `not_configured`.

## Jornada de frontend proposta

```mermaid
flowchart LR
    Inicio["Escolher local, datas e unidade"] --> Consulta["Consultar API"]
    Consulta --> Resultado["Previsão e risco heurístico"]
    Consulta --> Erro["Erro com ação de recuperação"]
    Resultado --> Qualidade["Mostrar fonte, coleta e qualidade"]
    Qualidade --> Alertas["Mostrar estado separado dos alertas oficiais"]
```

O frontend deve exibir valores `null` como indisponíveis, sinalizar stale,
mostrar o período/local retornados e manter o aviso da estimativa visível.
`not_configured` e `unavailable` não significam ausência de alertas reais.
O contrato atual não oferece lista de cidades para desambiguação: o geocoder
seleciona o primeiro resultado utilizável.
