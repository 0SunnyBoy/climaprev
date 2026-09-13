# Restrições funcionais, técnicas e de informação

**Data:** 2026-09-13. Regras implementadas e lacunas estão identificadas
explicitamente. [Índice](../PROJECT.md).

## Entrada e escopo

| ID     | Restrição                                                                    | Estado / consequência                                                            |
| ------ | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| RES-01 | Informar texto de local ou par completo de coordenadas, nunca ambos.         | Implementada no schema HTTP.                                                     |
| RES-02 | Texto com 1–200 caracteres e não vazio após trim.                            | Implementada; não há filtro de dados pessoais ou desambiguação interativa.       |
| RES-03 | Latitude entre -90 e 90; longitude entre -180 e 180.                         | Implementada para entrada do cliente.                                            |
| RES-04 | Período entre um e sete dias inclusivos; fim não anterior ao início.         | Implementada no schema HTTP; `DatePeriod` no domínio só valida a ordem.          |
| RES-05 | Unidade de temperatura: `celsius` ou `fahrenheit`.                           | Implementada; chuva, vento e umidade mantêm suas unidades.                       |
| RES-06 | Disponibilidade das datas depende do endpoint meteorológico.                 | Não há validação de início relativo a hoje ou do horizonte aceito pelo provedor. |
| RES-07 | Não há autenticação, histórico, mapas, app mobile, notificações ou ML. | Fora da implementação disponível.                                                |
| RES-08 | Não há integração real com alertas oficiais.                                 | A aplicação retorna `not_configured`; não é ausência confirmada de alertas.      |

Base: [schema](../src/climaprev/api/schemas/risk.py),
[modelos](../src/climaprev/domain/models.py), [composição](../src/climaprev/main.py).

## Política de risco existente

A política [reference-v1](../src/climaprev/domain/risk_policy.py) usa os
limiares abaixo. Eles descrevem o código e não representam validação
científica regional ou critérios oficiais de emissão de alertas.

| Medida                         | Moderado    | Alto        |
| ------------------------------ | ----------- | ----------- |
| Máxima de precipitação horária | ≥ 20 mm/h   | ≥ 30 mm/h   |
| Acumulado diário de chuva      | ≥ 30 mm/dia | ≥ 50 mm/dia |
| Rajada máxima                  | ≥ 40 km/h   | ≥ 61 km/h   |
| Temperatura máxima             | ≥ 35 °C     | ≥ 40 °C     |
| Temperatura mínima             | ≤ 5 °C      | ≤ 0 °C      |

O [avaliador](../src/climaprev/domain/risk_evaluator.py) prioriza a severidade
alta, seleciona uma condição por tipo no período e usa valor absoluto e
unidade como desempate. O resultado é `high` se houver condição alta,
`moderate` se houver outra condição e `low` se nenhuma for selecionada.

As condições são `heavy_rain_proxy`, `flooding_risk_proxy`,
`strong_wind_proxy` e `temperature_extreme_proxy`. O indicador de alagamento
reutiliza o candidato de chuva: não considera drenagem, relevo, nível de rios,
maré, solo ou vulnerabilidade local. O indicador de temperatura extrema não
é classificação de onda de calor. Não há probabilidade calibrada de desastre.

**Restrição de apresentação:** não traduzir `low` como “local seguro”. Dados
nulos podem impedir o disparo de condições e ainda resultar em `low`.
Sempre apresentar qualidade, fonte, período e aviso junto ao nível.

## Qualidade e interpretação

| ID     | Comportamento encontrado                                                                          | Limite ou pendência                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| RES-09 | Média de temperatura calculada das amostras horárias não nulas.                                   | Sem amostras, permanece `null`; amostragem parcial é sinalizada.                                      |
| RES-10 | `completeness` distingue complete, partial e unavailable; ausências aparecem em `missing_fields`. | Nenhuma entrada utilizável impede uma classificação conclusiva na interface.                          |
| RES-11 | Cobertura segue dias civis no fuso efetivo, incluindo 23/25 horas.                                | Lacunas são incompletude; excesso, ordem incompatível e horários fora do período são inválidos.       |
| RES-12 | Resposta projeta o fuso validado do provedor, também no cache hit.                                | Fuso inválido produz `WEATHER_DATA_INVALID`.                                                          |
| RES-13 | Chave v2 usa coordenadas sem arredondamento, período, normalização e destino do provedor.         | Nome e unidade de saída não fragmentam o cache canônico.                                              |
| RES-14 | Números devem ser finitos, percentuais de 0–100, chuva/vento não negativos e mínima ≤ máxima.     | Valores fora do contrato produzem 502 antes da avaliação/cache. Não é validação científica dos dados. |
| RES-15 | Risco consolida condições por tipo no período, sem data em cada condição.                         | Não oferece linha do tempo de risco diário.                                                           |

Base: [adaptador](../src/climaprev/infrastructure/providers/open_meteo.py) e
[serviço](../src/climaprev/application/services/forecast_query.py).

## Limites operacionais

| Parâmetro                       | Valor padrão no código                        | Observação                                                                                |
| ------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Cache de geocodificação         | 24 h                                          | Não há janela adicional de stale.                                                         |
| Cache de previsão fresca        | 600 s                                         | Contados da gravação no cache.                                                            |
| Expiração total da previsão     | 900 s                                         | São 15 min totais, não 10 + 15 min.                                                       |
| Lock de previsão                | 10 s                                          | Renovado a cada 5 s.                                                                      |
| Espera pelo lock                | Até 30 s                                      | Polling a cada 10 ms. Não é timeout global da requisição.                                 |
| Timeout HTTP de conexão/pool    | 2 s                                           | Por tentativa.                                                                            |
| Timeout HTTP de leitura/escrita | 5 s                                           | Por operação; não representa deadline total da consulta.                                  |
| Retries adicionais              | 2                                             | Até três tentativas; timeout, erro de rede e 5xx.                                         |
| Backoff                         | 50 ms, depois 100 ms                          | Não há retry de 4xx do provedor.                                                          |
| Timeout de socket Redis         | 1 s                                           | Configurado para conexão e operações.                                                     |
| Rate limit                      | Reposição de 60 tokens em 60 s; capacidade 10 | Token bucket: burst inicial 10, depois cerca de 1 token/s, não janela fixa de 60 pedidos. |
| Cota externa por destino | Reposição de 60 tokens em 60 s; capacidade 60 | Compartilhada por ambiente/destino, cobrada antes de cada tentativa. Homologação exige valores explícitos do operador. |

Evidências: [serviço](../src/climaprev/application/services/forecast_query.py),
[configuração](../src/climaprev/config.py),
[HTTP](../src/climaprev/infrastructure/http/client.py) e
[limiter](../src/climaprev/infrastructure/rate_limit/redis_rate_limiter.py).

O fallback stale é revalidado após espera/retries e imediatamente antes da
entrega, inclusive após alertas opcionais. Redis indisponível interrompe a consulta com 503; não existe
modo implementado que ignore cache, lock e rate limit para seguir sem Redis.
Também não há um circuit breaker ativo: o registro `dependency_circuit_state`
é telemetria de readiness e não bloqueia chamadas de forma autônoma.

## Restrições de configuração e exposição

- `CLIMAPREV_ENVIRONMENT=production` impede wildcard de CORS, mas não ativa
  automaticamente HTTPS, autenticação, ACL ou configurações de produção.
- Limites/janela/burst são positivos; timeouts também devem ser finitos.
  `additional_retries` rejeita negativos e limita o máximo em dois. O atraso
  sintético do perfil load pode ser zero.
- O Compose passa apenas parte das configurações ao serviço `app`.
  Adicionar uma variável ao `.env` não a injeta automaticamente no contêiner;
  ela precisa estar no `environment`/`env_file` do serviço.
- Não publicar perfil `load`, mock e limites de carga como ambiente de usuário.
- Namespace por ambiente não é isolamento de segurança nem de capacidade.
- A homologação omite query/IP/payload dos logs, bloqueia métricas internas
  na entrada TLS e aplica retenção de até sete dias. Logs operacionais podem
  perder eventos durante indisponibilidade/saturação; não são auditoria durável.
  Esses controles não configuram automaticamente outras implantações.

## Critérios para ampliar o produto

Antes de oferecer dados privados, definir identidade e autorização no backend.
Antes de oferecer histórico/notificações, definir consentimento de produto,
dados armazenados, retenção, exclusão e destinatários. Antes de exibir alertas
oficiais, definir fonte, cobertura geográfica/temporal e semântica de falha.
Esses são requisitos propostos de projeto; nenhuma dessas funcionalidades
integra o ciclo atual de implementação.
