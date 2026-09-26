# Validação e calibração da previsão

## Estado atual

O ClimaPrev recebe a previsão do provedor meteorológico e aplica a política
heurística `reference-v1`. A avaliação considera os dados horários disponíveis,
além dos totais diários, e produz uma avaliação para cada dia do período.

O resultado também informa o(s) dia(s) de maior risco. Quando existe empate no
maior nível, todas as datas empatadas são apresentadas. Isso evita que um risco
relevante fique escondido por uma média do período.

As localidades são aceitas somente com latitude e longitude finitas dentro dos
limites geográficos e com fuso horário IANA válido. Isso evita que uma resposta
de geocodificação ou coordenadas diretas contaminem a avaliação diária.

Alertas oficiais têm prioridade no resumo apresentado ao usuário. A estimativa
heurística continua sendo mantida separadamente para transparência e auditoria.

## Protocolo de validação histórica

A validação não deve usar dados inventados nem substituir avaliação técnica.
Para cada caso histórico revisado, o conjunto de dados deve conter:

1. localização, fuso horário e período consultado;
2. previsão que estaria disponível no momento da consulta;
3. observação posterior revisada por uma fonte confiável;
4. nível observado (`low`, `moderate` ou `high`);
5. indicação de dados ausentes, alertas oficiais e condições relevantes.

O módulo `climaprev.domain.risk_validation` compara a classificação da política
com o nível observado e calcula:

- quantidade de casos;
- acertos;
- falsos positivos;
- falsos negativos;
- acurácia;
- versão da política avaliada.

Os falsos negativos devem receber prioridade na revisão, pois representam um
risco real que não foi sinalizado.

### Coleta automatizada, sem banco

O comando `python -m climaprev.tools.validate_historical` executa uma amostra
offline limitada a 31 dias. Ele combina:

- `Previous Runs API`, com previsões arquivadas em antecedência fixa de 1 a 7
  dias;
- `Historical Weather API`, com o histórico observado/reanalisado para o mesmo
  local e período;
- a política `reference-v1`, aplicada aos dois conjuntos no mesmo formato.

Exemplo:

```bash
mkdir -p .historical-reports
docker compose run --rm -v "${PWD}/.historical-reports:/app/.historical-reports" app \
  python -m climaprev.tools.validate_historical \
  --latitude -1.4558 --longitude -48.5044 \
  --start 2025-01-01 --end 2025-01-31 --lead-days 1 \
  --output /app/.historical-reports/belem-lead-1.json
```

No PowerShell, o mesmo fluxo pode ser executado assim:

```powershell
New-Item -ItemType Directory -Force .historical-reports | Out-Null
$reports = (Resolve-Path .historical-reports).Path
docker compose run --rm --mount "type=bind,source=$reports,target=/app/.historical-reports" app `
  python -m climaprev.tools.validate_historical `
  --latitude -1.4558 --longitude -48.5044 `
  --start 2025-01-01 --end 2025-01-31 --lead-days 1 `
  --output /app/.historical-reports/belem-lead-1.json
```

O arquivo gerado é local e ignorado pelo Git. A ferramenta não é uma rota da
API pública, não grava resultados no Redis e não cria banco de dados. O
histórico climático de longa duração serve para análise de condições; para
medir habilidade de previsão, devem ser usados os snapshots arquivados de
previsões, pois eles preservam a antecedência original.

## Calibração estatística

Existe uma camada de calibração opcional em
`climaprev.domain.bias_correction`. Ela aceita um perfil revisado para ajustar
temperatura, precipitação e vento. O perfil padrão é `disabled` e não altera os
dados do provedor.

Um perfil só deve ser ativado depois de:

- possuir amostra histórica suficiente;
- ser comparado contra `reference-v1`;
- demonstrar redução de falsos negativos sem aumento injustificado de falsos
  positivos;
- ser versionado e registrado;
- manter `reference-v1` como fallback imediato.

Sem essa evidência, a aplicação deve permanecer com a previsão original. Isso
evita que uma correção estatística baseada em poucos dados piore o resultado.

O identificador da versão do perfil participa da chave de cache. Assim, uma
calibração revisada não reaproveita silenciosamente um resultado calculado com
outro perfil. O perfil `disabled` mantém o comportamento atual e o fallback
continua sendo a previsão original do provedor.

## Comunicação ao usuário

O frontend exibe:

- risco geral do período;
- origem da prioridade (`forecast_heuristic` ou `official_alert`);
- dia(s) de maior risco;
- condições que motivaram a avaliação;
- qualidade e ausência de dados;
- alertas oficiais separados da estimativa interna.

Nenhum desses dados deve ser apresentado como garantia ou como substituto de
orientação das autoridades competentes.
