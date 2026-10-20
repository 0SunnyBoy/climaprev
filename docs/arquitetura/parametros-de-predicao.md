# Parâmetros de predição

**Revisão 20/10/2026:** política reference-v1 ativa; sem calibração/promoção. As datas públicas devem estar entre hoje UTC e +6, com no máximo sete dias consecutivos. API valida antes do serviço e calendário acompanha o corte UTC; dias meteorológicos mantêm fuso local. 14 dias apenas planejado. Exemplos com datas fixas abaixo ilustram o contrato e devem ser atualizados para a janela vigente antes da execução. [Estado](../projeto/STATE.md).

Este documento descreve os parâmetros usados pelo Clima Prev para consultar
uma previsão meteorológica e produzir `forecast_risk`. Ele distingue os dados
enviados pelo usuário dos campos meteorológicos internos e dos limiares da
política de risco.

O comportamento descrito corresponde ao código atual. Os caminhos citados
apontam para a implementação de referência:

- [`RiskQueryParams`](../../src/climaprev/api/schemas/risk.py): validação da
  entrada HTTP.
- [`OpenMeteoForecastClient`](../../src/climaprev/infrastructure/providers/open_meteo.py):
  solicitação e normalização dos dados meteorológicos.
- [`RiskPolicy`](../../src/climaprev/domain/risk_policy.py): limiares usados
  pela política `reference-v1`.
- [`RiskEvaluator`](../../src/climaprev/domain/risk_evaluator.py): cálculo da
  severidade e do nível consolidado.

## Parâmetros enviados pelo usuário

O endpoint principal é `POST /api/v1/risk`. O endpoint `GET /api/v1/risk`
aceita os mesmos campos como parâmetros de consulta.

| Parâmetro | Tipo | Obrigatório | Regras e efeito |
| --- | --- | --- | --- |
| `location_text` | string | Uma forma de local | Texto entre 1 e 200 caracteres. O sistema remove espaços nas extremidades e resolve a localidade por geocodificação. |
| `latitude` | número | Junto com `longitude` | Deve estar entre `-90` e `90`. |
| `longitude` | número | Junto com `latitude` | Deve estar entre `-180` e `180`. |
| `start_date` | data ISO | Sim | Data inicial no formato `YYYY-MM-DD`. |
| `end_date` | data ISO | Não | Se omitida, recebe o valor de `start_date`. Deve ser igual ou posterior à data inicial. |
| `temperature_unit` | `celsius` ou `fahrenheit` | Não | Default: `celsius`. Controla a unidade das temperaturas retornadas; o cálculo de risco continua em Celsius. |

### Regras de localização

- Use `location_text` **ou** o par `latitude`/`longitude`.
- Não combine texto de localidade com coordenadas.
- Coordenadas devem ser fornecidas em conjunto.
- O período pode conter no máximo sete dias consecutivos, contando a data
  inicial e a final.
- Uma localidade não encontrada produz erro `404`; entrada inválida produz
  erro `422`.

Exemplos:

```json
{
  "location_text": "São Paulo, SP",
  "start_date": "2026-09-18",
  "end_date": "2026-09-20",
  "temperature_unit": "celsius"
}
```

```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "start_date": "2026-09-18",
  "temperature_unit": "fahrenheit"
}
```

## Parâmetros internos da consulta meteorológica

Depois da validação, o serviço transforma a entrada em uma localização
canônica e em um período. O adaptador Open-Meteo envia estes parâmetros, que
não são editáveis diretamente pelo usuário:

| Parâmetro do provedor | Valor usado | Finalidade |
| --- | --- | --- |
| `latitude` | Latitude canônica | Ponto da previsão. |
| `longitude` | Longitude canônica | Ponto da previsão. |
| `start_date` | Data inicial validada | Início da janela consultada. |
| `end_date` | Data final validada | Fim da janela consultada. |
| `timezone` | `auto` | Faz o provedor devolver séries alinhadas ao fuso do local. |
| `temperature_unit` | `celsius` | Mantém os limiares de temperatura em uma unidade única. |
| `precipitation_unit` | `mm` | Unidade usada para chuva diária e horária. |
| `wind_speed_unit` | `kmh` | Unidade usada para vento e rajadas. |

O adaptador solicita os seguintes campos meteorológicos:

- Diários: `temperature_2m_min`, `temperature_2m_max`,
  `precipitation_sum`, `precipitation_probability_max`,
  `wind_speed_10m_max`, `wind_gusts_10m_max` e `weather_code`.
- Horários: `temperature_2m`, `relative_humidity_2m`, `precipitation` e
  `precipitation_probability`.

O serviço normaliza esses campos por dia. A média de temperatura e umidade,
assim como os máximos horários de precipitação e probabilidade, são derivados
das séries horárias do período.

## Variáveis que influenciam o risco

O avaliador percorre cada dia da previsão e considera somente estas variáveis
para gerar condições de risco:

| Variável normalizada | Unidade | Uso na avaliação |
| --- | --- | --- |
| `precipitation_max_hourly_mm` | `mm/h` | Detecta o proxy de chuva intensa horária. |
| `precipitation_sum_mm` | `mm/day` | Detecta o proxy de chuva acumulada diária. |
| `wind_gust_max_kmh` | `km/h` | Detecta o proxy de vento forte. |
| `temperature_max_c` | Celsius | Detecta o proxy de temperatura máxima extrema. |
| `temperature_min_c` | Celsius | Detecta o proxy de temperatura mínima extrema. |

Os demais campos da previsão, como umidade média, probabilidade de
precipitação, velocidade máxima do vento e código meteorológico, são
retornados para contexto e qualidade dos dados, mas não alteram diretamente o
nível atual de `forecast_risk`.

## Política de risco atual

A política ativa é `reference-v1`. Ela usa limiares de referência, não uma
probabilidade estatística nem uma classificação oficial. A avaliação ocorre
em Celsius, `mm` e `km/h`, independentemente da unidade escolhida para a
resposta.

| Condição | Moderado a partir de | Alto a partir de | Unidade |
| --- | ---: | ---: | --- |
| Chuva horária | `20` | `30` | `mm/h` |
| Chuva diária acumulada | `30` | `50` | `mm/day` |
| Rajada de vento | `40` | `61` | `km/h` |
| Temperatura máxima | `35` | `40` | `°C` |
| Temperatura mínima | `5` ou menos | `0` ou menos | `°C` |

Para chuva, vento e temperatura máxima, o valor atinge a severidade quando é
maior ou igual ao limiar. Para temperatura mínima, a severidade ocorre quando
o valor é menor ou igual ao limiar.

### Consolidação do resultado

1. O sistema avalia cada dia do período.
2. Para cada tipo de condição, mantém a ocorrência de maior severidade. Em
   caso de empate, mantém o maior valor absoluto.
3. Chuva que gera uma condição também cria `flooding_risk_proxy` com a mesma
   severidade e valor. Esse campo é um indicador de precipitação, não uma
   avaliação hidrológica local.
4. O nível final é `high` se qualquer condição for alta, `moderate` se houver
   alguma condição moderada e nenhuma alta, ou `low` se nenhuma condição for
   gerada.
5. `forecast_risk.daily` preserva o nível e as condições de cada dia.
6. `forecast_risk.peak_days` lista todos os dias empatados no maior nível de
   risco identificado. O frontend destaca essas datas ao usuário.
7. `risk_overview` resume o risco efetivo para apresentação. Quando existem
   alertas oficiais, sua fonte passa a ser `official_alert`; a avaliação
   heurística continua disponível em `forecast_risk`.
8. A chave de cache inclui a identidade do provedor, a normalização e a versão
   do perfil de calibração. Isso impede misturar respostas produzidas por
   configurações estatísticas diferentes.

As condições retornadas usam estes tipos:

- `heavy_rain_proxy`, para chuva horária ou diária acima dos limiares;
- `flooding_risk_proxy`, como sinal derivado da chuva;
- `strong_wind_proxy`, para rajadas acima dos limiares;
- `temperature_extreme_proxy`, para máximas ou mínimas extremas.

## Conversão de temperatura

O provedor e o avaliador trabalham em Celsius. Quando o usuário escolhe
`fahrenheit`, o serviço converte somente os campos de temperatura da resposta
com:

```text
fahrenheit = celsius × 9 / 5 + 32
```

Valores de chuva, vento, umidade e probabilidade não são convertidos pela
opção `temperature_unit`.

## Dados ausentes e limitações

- Um campo meteorológico ausente não é transformado em zero.
- Se faltar uma variável necessária para uma condição, essa condição não é
  criada para aquele dia.
- A resposta informa `data_quality.completeness` como `complete`, `partial`
  ou `unavailable` e lista os campos ausentes.
- A política `reference-v1` é uma heurística de interpretação de previsão. Ela
  não substitui alerta oficial, avaliação hidrológica, orientação médica ou
  instrução de Defesa Civil.
- `official_alerts` é uma seção separada da resposta. Sua presença altera a
  prioridade do resumo em `risk_overview`, mas não apaga o resultado heurístico.
- A validação histórica e o protocolo de calibração estão descritos em
  [`validacao-e-calibracao.md`](validacao-e-calibracao.md).

Qualquer alteração dos limiares, das variáveis consideradas ou da unidade de
avaliação deve atualizar a versão da política, os testes de domínio e este
documento.
