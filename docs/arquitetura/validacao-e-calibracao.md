# Validação e calibração da previsão

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.
>
> Reference-v1 permanece ativa, sem candidata calibrada/promovida. CSVs de três estações, baseline de cinco eventos, comparação espacial e diagnóstico horário concluídos tecnicamente, com resultados mistos e sem ganho substancial comprovado. Revisão científica/aceite pendentes; evolução da candidate-1 por último, focada em qualidade e precisão da previsão. Não confundir classificação com melhoria dos valores meteorológicos.

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

O módulo `climaprev.domain.risk_validation` mantém o relatório básico legado.
O comparador experimental usa `climaprev.domain.verification` para calcular:

- matriz de confusão (`low`, `moderate`, `high`; linhas = referência,
  colunas = previsão), acurácia e precisão/recall/F1 por classe;
- detecção de pelo menos `moderate` e de `high`, com omissões, falsos alarmes,
  razão de falsos alarmes e taxa de falsos positivos;
- viés (`previsto - referência`), MAE e RMSE dos valores meteorológicos;
- resultados por evento e estratos de localidade, antecedência e mês;
- configuração, hashes, contagens elegíveis e exclusões.

Uma razão com denominador zero é `null`, não evidência de desempenho perfeito
nem erro igual a zero. As contagens de suporte precisam acompanhar a leitura
de cada métrica. O `report` legado da coleta conserva o formato anterior;
para analisar ausência de casos e métricas indefinidas, use `comparison`.

Os falsos negativos devem receber prioridade na revisão, pois representam um
risco real que não foi sinalizado.

### Coleta automatizada, sem banco

O comando `python -m climaprev.tools.validate_historical` coleta uma janela
limitada a 31 dias e pode salvar suas entradas para avaliação offline. Ele combina:

- `Previous Runs API`, com previsões arquivadas em antecedência fixa de 1 a 7
  dias;
- `Historical Weather API`, com reanálise para o mesmo local e período;
- `reference-v1` aplicada à previsão e, como alvo heurístico congelado, à
  reanálise. Esse alvo é identificado como `reference-v1-on-reanalysis`.

Reanálise não é um registro independente de desastres ou impactos. O diagnóstico
mede concordância meteorológica/heurística, sem demonstrar habilidade de prever
impactos reais. Aplicar a v1 à reanálise também não valida seus próprios limiares;
essa limitação permanece ao comparar uma candidata com esse alvo.

Reconstrua a imagem após mudanças nos módulos (`docker compose build app`).
Exemplo:

```bash
mkdir -p .historical-reports
docker compose run --rm -v "${PWD}/.historical-reports:/app/.historical-reports" app \
  python -m climaprev.tools.validate_historical \
  --latitude -1.4558 --longitude -48.5044 \
  --start 2025-01-01 --end 2025-01-31 --lead-days 1 \
  --timezone America/Belem --forecast-model gfs_global --observed-model era5 \
  --minimum-coverage 1.0 \
  --save-input /app/.historical-reports/belem-2025-01-lead-1-input.json \
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
  --timezone America/Belem --forecast-model gfs_global --observed-model era5 `
  --minimum-coverage 1.0 `
  --save-input /app/.historical-reports/belem-2025-01-lead-1-input.json `
  --output /app/.historical-reports/belem-lead-1.json
```

Use também antecedências 3 e 7, com nomes de arquivo próprios. São janelas de
diagnóstico propostas, sem resultado presumido e sem representatividade
geográfica, sazonal ou de eventos demonstrada. A disponibilidade de cada
modelo/variável/período deve ser verificada na coleta.

A cobertura padrão é 100% das horas esperadas da variável que sustenta cada
evento, em previsão e reanálise. Chuva horária/diária, rajada e temperatura
máxima/mínima têm elegibilidade separada; o resultado geral exige todos os
eventos elegíveis. Dados ausentes não viram zero. O normalizador registra
horas válidas/esperadas e as exclusões. Umidade e código meteorológico também
são solicitados e normalizados, mas não determinam a elegibilidade desses
cinco eventos. A contagem horária respeita o dia civil no fuso informado.

O snapshot contém respostas brutas, configuração, URLs/parâmetros, horário
da coleta, identidade do alvo e hashes dos algoritmos de avaliação. Unidades
horárias explícitas são verificadas; unidades incompatíveis são rejeitadas.
O replay recusa algoritmos diferentes dos registrados, exigindo migração
explícita do dataset quando o pipeline muda. O envelope verifica SHA-256 na leitura e
recusa sobrescrever conteúdo diferente. Hash comprova consistência com o
conteúdo registrado, não autenticidade da fonte; alguém pode alterar o
conteúdo e recalcular o hash. Preserve os artefatos e a revisão do código
usado junto do relatório. Não há assinatura nem prova de autenticidade.

Para reproduzir sem rede, use somente o snapshot e um destino de relatório:

```powershell
docker compose run --rm --mount "type=bind,source=$reports,target=/app/.historical-reports" app `
  python -m climaprev.tools.validate_historical `
  --input /app/.historical-reports/belem-2025-01-lead-1-input.json `
  --output /app/.historical-reports/belem-lead-1-replay.json
```

`--input` não deve ser combinado com parâmetros de coleta ou `--save-input`.
Os arquivos em `.historical-reports/` são locais e ignorados pelo Git. A
ferramenta não é uma rota pública, não grava no Redis e não cria banco.

### Comparação de experimentos separados

`python -m climaprev.tools.compare_historical` lê um ou mais snapshots sem
rede. Mantém o mesmo alvo congelado e casos elegíveis para todas as variantes:

| Variante | Previsão | Política |
| --- | --- | --- |
| R0 | Original | `reference-v1` |
| A, se `--candidate` | Original | Candidata experimental |
| B, se `--calibration` | Calibrada | `reference-v1` |
| AB, se ambas as opções | Calibrada | Candidata experimental |

Para executar apenas o diagnóstico da baseline, sem inventar parâmetros de
candidata/calibração:

```powershell
docker compose run --rm --mount "type=bind,source=$reports,target=/app/.historical-reports" app `
  python -m climaprev.tools.compare_historical `
  --input /app/.historical-reports/belem-2025-01-lead-1-input.json `
  --protocol docs/planejamento/reference-candidate-1/protocolo-piloto.json `
  --partition diagnostic `
  --output /app/.historical-reports/belem-diagnostic.json
```

Depois de definir e registrar configurações justificadas, a forma do comando
é a seguinte. Os arquivos `candidate.json` e `calibration.json` são entradas
que precisam ser preparados; este exemplo não fornece ajustes aprovados:

```powershell
python -m climaprev.tools.compare_historical `
  --input .historical-reports/belem-2025-01-lead-1-input.json .historical-reports/belem-2025-01-lead-3-input.json `
  --candidate .historical-reports/candidate.json `
  --calibration .historical-reports/calibration.json `
  --protocol docs/planejamento/reference-candidate-1/protocolo-piloto.json `
  --partition diagnostic --output .historical-reports/comparison.json
```

A candidata declara `policy_version` com prefixo `reference-candidate-` e
`thresholds` com todos os campos numéricos de `RiskPolicy`; limiares faltantes,
não finitos ou incoerentes são rejeitados. O perfil de calibração declara todos
os campos de `ForecastCalibration`: `profile_version`, `enabled` (true),
`temperature_offset_c`, `precipitation_multiplier` e `wind_multiplier`.
Sua identidade precisa diferir de `disabled`.

O protocolo admite splits `adjustment`, `validation` e `test`, com `start` e
`end` cronológicos e disjuntos. `--partition` seleciona um desses intervalos
ou `diagnostic` (sem filtro temporal de partição). A validação estrutural do
CLI não aprova o desenho científico nem garante que o teste permaneceu
reservado. O [protocolo piloto](../planejamento/reference-candidate-1/protocolo-piloto.md)
contém um exemplo proposto, ainda pendente de aprovação; o piloto usa somente
`diagnostic`. Mesmo para `--partition test`, a ferramenta não autoriza promoção.

Nenhum comando altera automaticamente política, calibração ou configuração
da API. Resultados têm decisão `diagnostic_only_not_approved`. Ainda faltam
metas de promoção, suficiência amostral, avaliação de incerteza e revisão
especializada para uma decisão científica.

### Ambiente local Windows

Docker continua sendo o ambiente principal de reprodução. Para executar os
comandos diretamente em um ambiente Python Windows já provisionado:

```powershell
python -m pip install --require-hashes -r requirements-windows-dev.lock
$env:PYTHONPATH = (Resolve-Path src).Path
```

Esse complemento inclui `requirements-dev.lock` e fixa `colorama`/`tzdata`
para Windows. `tzdata` fornece os fusos IANA usados pelo normalizador. Não
substitui os locks Linux nem altera a imagem de produção.

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
