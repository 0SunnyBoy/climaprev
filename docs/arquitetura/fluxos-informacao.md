# Fluxos de informação e contrato de integração

**Base:** código local em 2026-09-18. [Índice](../projeto/PROJECT.md).

## Inventário de transferências

| ID     | Origem → destino      | Informações transmitidas                                                       | Finalidade                              |
| ------ | --------------------- | ------------------------------------------------------------------------------ | --------------------------------------- |
| INF-01 | Cliente → API         | Texto de local ou coordenadas, datas, unidade e `X-Request-ID` opcional.       | Solicitar previsão e risco.             |
| INF-02 | Conexão/proxy → API   | IP do peer e, somente se confiável, cadeia `X-Forwarded-For`.                  | Identificar cliente para limite de uso. |
| INF-03 | API → Geocoding       | `name` com texto do local e `language=pt`.                                     | Buscar localidade.                      |
| INF-04 | Geocoding → API       | Resultados com nome, latitude, longitude, fuso e contexto.                    | Exibir até cinco sugestões.             |
| INF-05 | API → Forecast        | Coordenadas, datas, `timezone=auto`, unidades e variáveis diárias/horárias.    | Obter previsão meteorológica.           |
| INF-06 | Forecast → API        | JSON com fuso, datas e séries meteorológicas.                                  | Validar e normalizar.                   |
| INF-07 | API ↔ Redis           | Local, previsão, timestamps, tokens de lock, limite por IP e cota por destino. | Cache e coordenação.                    |
| INF-08 | Aplicação → domínio   | Previsão normalizada e política de risco.                                      | Calcular estimativa sem rede.           |
| INF-09 | API → cliente         | Local, período, dias, risco, alertas, qualidade, fonte, aviso e ID.            | Apresentar resultado rastreável.        |
| INF-10 | API → observabilidade | Rota, status, duração, cache, provider, retries, erro e ID.                    | Diagnóstico operacional.                |
| INF-11 | API → INMET           | Coordenadas, período e localização canônica.                                  | Consultar avisos ativos.                |
| INF-12 | INMET → API           | Eventos, severidade, vigência, área e URL de origem.                           | Apresentar alertas separados do risco. |

O código não repassa `X-Forwarded-For`, identidade do usuário ou request ID nas
chamadas Open-Meteo. O serviço externo recebe os parâmetros meteorológicos e
observa a conexão de saída do servidor. Por usar query string, a entrada do
cliente também pode aparecer em histórico do navegador e logs de acesso de
servidores/proxies, conforme sua configuração.

## Entrada HTTP implementada

`GET /api/v1/risk` e `POST /api/v1/risk`, sem autenticação implementada.
`GET /api/v1/locations/search` oferece sugestões de localidades.

| Campo              | Tipo     | Regra                                                                           |
| ------------------ | -------- | ------------------------------------------------------------------------------- |
| `location_text`    | string   | Alternativa às coordenadas; 1–200 caracteres, sem texto vazio após trim.        |
| `latitude`         | número   | De -90 a 90, exige longitude.                                                   |
| `longitude`        | número   | De -180 a 180, exige latitude.                                                  |
| `start_date`       | data ISO | Obrigatória, `YYYY-MM-DD`.                                                      |
| `end_date`         | data ISO | Opcional; assume início, deve ser igual ou posterior, até sete dias inclusivos. |
| `temperature_unit` | enum     | `celsius` padrão ou `fahrenheit`.                                               |

`location_text` e coordenadas são mutuamente exclusivos. Não enviar CPF,
nome de pessoa, e-mail, token ou endereço residencial no texto do local.
Esta última orientação é uma restrição de uso proposta: não existe filtro
de dados pessoais no campo livre.

Exemplos de formato; as datas não garantem disponibilidade no provedor:

```http
GET /api/v1/risk?location_text=Belem&start_date=2026-09-13&end_date=2026-09-15&temperature_unit=celsius
X-Request-ID: consulta-exemplo-001
```

```http
GET /api/v1/risk?latitude=-1.4558&longitude=-48.4902&start_date=2026-09-13
```

```http
POST /api/v1/risk
Content-Type: application/json

{"location_text":"Belém, Pará","start_date":"2026-09-13","temperature_unit":"celsius"}
```

## Saída HTTP implementada

| Campo              | Conteúdo e uso                                                        |
| ------------------ | --------------------------------------------------------------------- |
| `request_id`       | Correlação da consulta; não é autenticação nem identidade de usuário. |
| `location`         | `name`, `latitude`, `longitude`, `timezone`, `source`.                |
| `period`           | `start_date` e `end_date` efetivos.                                   |
| `temperature_unit` | Unidade das temperaturas devolvidas.                                  |
| `days`             | Lista de dias com os campos da tabela seguinte.                       |
| `forecast_risk`    | `level`, `method`, `policy_version` e `conditions`.                   |
| `official_alerts`  | `status` e `items`, separados do risco calculado.                     |
| `data_quality`     | `is_stale`, `missing_fields` e `completeness`.                        |
| `source`           | `provider` e `fetched_at`, horário de coleta pelo backend.            |
| `disclaimer`       | Aviso de que a estimativa não substitui alertas oficiais.             |

`cache_status` é interno ao serviço/log e não faz parte do JSON público.
`fetched_at` não é a data de emissão do modelo meteorológico.

| Campo de cada dia                    | Unidade                 | Origem / transformação atual                                            |
| ------------------------------------ | ----------------------- | ----------------------------------------------------------------------- |
| `date`                               | Data ISO                | Série diária do provedor.                                               |
| `temperature_min`, `temperature_max` | Celsius ou Fahrenheit   | Mínima/máxima diária; conversão somente na saída.                       |
| `temperature_mean`                   | Celsius ou Fahrenheit   | Média das amostras horárias não nulas; `null` sem amostras.             |
| `humidity_mean_pct`                  | %                       | Média das amostras horárias não nulas do dia.                           |
| `precipitation_sum_mm`               | mm                      | Acumulado diário.                                                       |
| `precipitation_probability_max_pct`  | %                       | Máxima das probabilidades horárias; não usa o campo diário equivalente. |
| `precipitation_max_hourly_mm`        | mm no intervalo horário | Máxima das amostras horárias de precipitação.                           |
| `wind_max_kmh`                       | km/h                    | Máxima diária de velocidade.                                            |
| `wind_gust_max_kmh`                  | km/h                    | Máxima diária de rajada.                                                |
| `weather_code`                       | Inteiro                 | Código diário recebido do provedor.                                     |

Os campos meteorológicos aceitam `null`; zero continua sendo um valor válido.
`missing_fields` identifica ausências por campo/dia e lacunas de cobertura.
`completeness=complete` exige todas as entradas de risco e cobertura horária
de chuva completa no período civil; dias de 23/25 horas são considerados.
`partial` indica entradas ou cobertura incompletas; `unavailable` significa
que nenhuma entrada de risco é utilizável. O nível `low` nesse último caso
não deve ser apresentado como avaliação conclusiva.

Cada condição de risco contém `type`, `severity`, `value`, `unit` e `reason`.
O nível global é `low`, `moderate` ou `high`; o método é `forecast_heuristic`
e a versão atual é `reference-v1`. O risco é agregado por período, sem data
individual em cada condição. Veja [restrições](../operacoes/restricoes.md).

Alertas oficiais têm os estados `available`, `not_configured` e `unavailable`.
Cada item previsto no contrato contém `source`, `event`, `severity`,
`effective_at`, `expires_at`, `geographic_scope` e `source_url`.
`expires_at` e `source_url` aceitam `null`. Na composição atual, o adaptador
consulta o INMET: `available` indica resposta válida e `unavailable` indica
falha da dependência. `not_configured` permanece para adaptadores opcionais
ou fixtures de teste, mas não é o estado padrão do app.

Exemplo realista do formato de erro, com valores ilustrativos:

```json
{
  "error": {
    "code": "INVALID_PERIOD",
    "message": "date period is invalid",
    "request_id": "consulta-exemplo-001"
  }
}
```

## Armazenamento, retenção e acesso

| Informação                         | Local / chave                                               | Retenção observada                                                        | Quem acessa no desenho atual                |
| ---------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------- |
| Texto consultado e local resolvido | Redis: `climaprev:{environment}:geo:v1:{texto-codificado}`  | 24 h após gravação.                                                       | Backend e quem tiver acesso ao Redis.       |
| Previsão canônica                  | Redis: `climaprev:{environment}:forecast:v2:{digest}`       | Fresca 10 min; expiração total 15 min.                                    | Backend e acesso ao Redis.                  |
| Alertas oficiais                   | Redis: `official-alerts:v1:{digest}`                         | Sucesso: 5 min fresco/10 min stale; falha: 30 s fresco/60 s stale.          | Backend e acesso ao Redis.                  |
| Token de atualização               | Redis: `climaprev:{environment}:lock:{chave-previsao}`      | 10 s, renovado enquanto a operação mantém propriedade.                    | Backend e acesso ao Redis.                  |
| IP e estado do limite              | Redis: `climaprev:{environment}:rate-limit:v1:{identidade}` | TTL de `burst × janela / limite`, renovado a cada tentativa; padrão 10 s. | Backend e acesso ao Redis.                  |
| Metadados do app e entrada | Homologação: socket Unix e arquivos JSONL do coletor; desenvolvimento: stdout sanitizado. | Homologação: teto de sete dias e 1 MiB por hora; desenvolvimento depende do destino. | Operação via volume dedicado. |
| Contadores                         | Memória de cada processo                                    | Até reiniciar o processo.                                                 | Operação via snapshot interno por processo. |

Na homologação, o coletor persiste somente evento, request ID, rota
normalizada, status, duração e horário de registro. Métricas de cache, retries
e risco ficam no snapshot em memória, sem retenção histórica automática.

A cota externa usa um namespace próprio por ambiente, identificador do destino
com hash e expiração do token bucket. Ela é compartilhada entre workers e
consumida a cada tentativa, incluindo geocodificação e retries. Esgotamento
produz 503 ou fallback de forecast ainda válido; Redis indisponível bloqueia
o envio. As métricas de requisição usam templates de rota e `unmatched`,
sem inserir caminhos arbitrários, query ou IP nas dimensões.

O texto da chave de geocodificação usa `casefold` e codificação de URL; isso
não é criptografia nem anonimização. O IP é armazenado diretamente na chave
do rate limit. Não existe histórico persistente de consultas nem isolamento
por usuário/tenant. TTL de cache não define retenção de logs, cópias ou backups.

O digest da previsão incorpora coordenadas sem arredondamento, período,
versão de normalização e destino do provedor. Nome de exibição e unidade de
saída não alteram a identidade. O local é recomposto para a consulta atual e
recebe o fuso efetivo do payload, inclusive no cache hit. Chaves v1 antigas
expiram naturalmente; a migração não faz limpeza global do Redis.

## Contrato da interface e de outros consumidores

A interface nativa consulta a API na mesma origem com `fetch`, usando
`credentials: omit` e `cache: no-store`. A consulta de risco envia JSON em
`POST /api/v1/risk`; a busca de localidades usa parâmetros na URL em
`GET /api/v1/locations/search`. O cliente envia cidade ou coordenadas, data
inicial, data final quando preenchida e unidade. O seletor de modo é local e
não integra a consulta. A operação assíncrona não adiciona os parâmetros à URL
da página nem grava histórico no aplicativo.

- Enviar somente os campos de entrada descritos e renderizar a projeção pública.
- Preservar unidades, fonte, qualidade e aviso; não recalcular risco no cliente.
- Mostrar indisponibilidade e dados desatualizados como estados distintos.
- Não tratar `low` como garantia de segurança nem lista vazia como alerta inexistente.
- Validar links de fontes antes de torná-los navegáveis. Quando o INMET retorna
  `available` sem itens, isso significa que a fonte não devolveu alertas
  aplicáveis à consulta, não que não existam alertas em toda a região.

Evidências: [schema](../../src/climaprev/api/schemas/risk.py),
[resposta](../../src/climaprev/api/routes/risk.py),
[adaptador](../../src/climaprev/infrastructure/providers/open_meteo.py),
[cache](../../src/climaprev/infrastructure/cache/redis_cache.py) e
[observabilidade](../../src/climaprev/api/observability.py).
