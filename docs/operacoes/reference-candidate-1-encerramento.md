# Reference-candidate-1: encerramento técnico e retorno à V1

Data: 28/10/2026. Branch local: `develop2`. Base: `7b09fe6`.

A implementação entrega o pipeline experimental, o registro da candidata e a
seleção operacional explícita. Os ensaios usam dados sintéticos e comprovam o
comportamento do software. **O estudo científico real e o parecer de promoção
continuam pendentes.** A aplicação padrão usa Open-Meteo, `reference-v1`,
normalização original e calibração `disabled`.

Nenhuma campanha real, promoção, publicação remota ou alteração de produção
foi realizada nesta entrega. Os aceites E1 (coleta), E2 (desenvolvimento/teste)
e E3 (seleção operacional) são registros de rastreabilidade fornecidos pelo
responsável; não constituem autenticação criptográfica da identidade humana.
Os registros dos testes dizem explicitamente `synthetic` e não autorizam uso real.

## Entregas e commits

O planejamento e as evidências detalhadas ficam locais em
`.specs/features/reference-candidate-1-tecnica/`, conforme a exclusão expressa
do repositório. Cada incremento de código tem um commit atômico com o ID da
tarefa e do requisito. Os testes abaixo estão versionados.

| Tarefa / requisito | Resultado | Commit local | Evidência de comportamento |
| --- | --- | --- | --- |
| T1 / RCT-01 | Validar o contrato do protocolo | `292fc2f` | [test_experimental_protocol.py](../../tests/unit/tools/test_experimental_protocol.py) |
| T2 / RCT-02 | Classificar casos por partição | `aab8106` | [test_experimental_protocol.py](../../tests/unit/tools/test_experimental_protocol.py) |
| T3 / RCT-03 | Bloquear execução por modo sem aceite | `b564023` | [test_experimental_protocol.py](../../tests/unit/tools/test_experimental_protocol.py) |
| T4 / RCT-04 | Gravar o envelope de evidências | `21319e4` | [test_experimental_archive.py](../../tests/unit/tools/test_experimental_archive.py) |
| T5 / RCT-05 | Validar capacidade por braço e variável | `92fbd9b` | [test_experimental_collection.py](../../tests/unit/tools/test_experimental_collection.py) |
| T6 / RCT-06 | Classificar evidência da rodada | `c28f1d4` | [test_experimental_collection.py](../../tests/unit/tools/test_experimental_collection.py) |
| T7 / RCT-07 | Identificar a família de origem | `b4d6064` | [test_experimental_collection.py](../../tests/unit/tools/test_experimental_collection.py) |
| T8 / RCT-08 | Validar a semântica das medições | `03554b6` | [test_experimental_collection.py](../../tests/unit/tools/test_experimental_collection.py) |
| T9 / RCT-09 | Importar temperatura instantânea observada | `8d43d54` | [test_experimental_observations.py](../../tests/unit/tools/test_experimental_observations.py) |
| T10 / RCT-10 | Parear extremos com equivalência explícita | `1ebeb69` | [test_experimental_variable_pairing.py](../../tests/unit/tools/test_experimental_variable_pairing.py) |
| T11 / RCT-11 | Importar vento e rajada separadamente | `0283223` | [test_experimental_observations.py](../../tests/unit/tools/test_experimental_observations.py) |
| T12 / RCT-12 | Importar umidade observada | `6bd6565` | [test_experimental_observations.py](../../tests/unit/tools/test_experimental_observations.py) |
| T13 / RCT-13 | Expandir o índice completo de alvos | `03918ef` | [test_experimental_progress.py](../../tests/unit/tools/test_experimental_progress.py) |
| T14 / RCT-14 | Ligar cobertura operacional a pares válidos | `1a30294` | [test_experimental_coverage.py](../../tests/unit/tools/test_experimental_coverage.py) |
| T15 / RCT-15 | Orquestrar o runner local com retomada explícita | `3b1ff6c` | [test_experimental_runner.py](../../tests/integration/tools/test_experimental_runner.py) |
| T16 / RCT-16 | Executar piloto sintético ponta a ponta | `02fb04d` | [test_experimental_pipeline.py](../../tests/integration/tools/test_experimental_pipeline.py) |
| T17 / RCT-17 | Comparar pares multivariáveis | `decf14d` | [test_experimental_variable_comparison.py](../../tests/unit/tools/test_experimental_variable_comparison.py) |
| T18 / RCT-18 | Integrar relatório de incerteza pareada | `7d7a9d9` | [test_experimental_uncertainty.py](../../tests/unit/tools/test_experimental_uncertainty.py) |
| T19 / RCT-19 | Separar D+7 e as coortes temporais | `548258a` | [test_experimental_variable_comparison.py](../../tests/unit/tools/test_experimental_variable_comparison.py) |
| T20 / RCT-20 | Exportar o relatório técnico consolidado | `dc99b3f` | [test_experimental_report.py](../../tests/unit/tools/test_experimental_report.py) |
| T21 / RCT-21 | Registrar a candidata congelável | `2788d7f` | [test_experimental_candidate.py](../../tests/unit/tools/test_experimental_candidate.py) |
| T22 / RCT-22 | Selecionar configuração apenas em desenvolvimento | `c7fa2f4` | [test_historical_experiment.py](../../tests/unit/tools/test_historical_experiment.py) |
| T23 / RCT-23 | Avaliar a candidata congelada no teste independente | `f8a49bf` | [test_historical_experiment.py](../../tests/unit/tools/test_historical_experiment.py) |
| T24 / RCT-24 | Registrar parecer e elegibilidade operacional | `6ae16d3` | [test_experimental_candidate.py](../../tests/unit/tools/test_experimental_candidate.py) |
| T25 / RCT-25 | Adaptar a estratégia candidata à porta de previsão | `3e6c4ad` | [test_candidate_forecast.py](../../tests/integration/providers/test_candidate_forecast.py) |
| T26 / RCT-26 | Compor seleção interna e retorno à baseline | `36bf920` | [test_candidate_selection.py](../../tests/integration/application/test_candidate_selection.py) |
| T27 / RCT-27 | Preservar a apresentação PT/EN do risco | `79e3e05` | [RiskSummary.test.ts](../../frontend/src/components/RiskSummary.test.ts) |
| T28 / RCT-28 | Dossiê, evidências e roteiro de retorno completo | Commit deste documento | [Ensaio de composição e rollback](../../tests/integration/application/test_candidate_selection.py) |

Para obter a revisão deste documento, execute
`git log -1 --format=%h -- docs/operacoes/reference-candidate-1-encerramento.md`.
A revisão independente final tem relatório local em
`.specs/features/reference-candidate-1-tecnica/validation.md`; sua conclusão
não deve ser inferida apenas das contagens abaixo.

## Verificações executadas

| Gate | Resultado observado |
| --- | --- |
| Backend completo, com warnings tratados como erro | 963 testes aprovados; baseline anterior de 757 testes. |
| Análise estática | Ruff aprovado; mypy aprovado em 87 módulos de produto. |
| Frontend | 56 testes aprovados em 10 arquivos; baseline anterior de 48 testes. |
| Frontend: lint, tipos e build | Aprovados usando o Dockerfile e lock existentes. |
| Dependências frontend | `npm audit --audit-level=high`: zero vulnerabilidades no momento do ensaio. |
| Navegador HTTP | Runner existente ampliado: candidata em PT/EN e C/F, null visível como indisponível, prioridade oficial, sem confiança individual derivada do estudo. API substituída por fixture neste teste de apresentação. |
| Navegador HTTPS | Dez verificações com API FastAPI real e provedor meteorológico sintético: consulta, CORS, TLS, janela de datas, acessibilidade, falha 503, limite 429 e indisponibilidade da API. |
| Navegador usado | Chrome `155.0.8059.79`; Playwright Python `1.63.0` e Node `1.62.1`, conforme runners. |
| Pacote runtime | Build pelo Dockerfile original; usuário 10001; ausência de testes, docs, arquivos de ambiente e ferramentas dev; hashes dos 87 módulos comparados ao checkout. |

Os ensaios não medem SLO ou carga de produção. A regressão preserva os contratos
de timeout, cache, alertas oficiais e janela pública existentes. As evidências
HTTPS desta execução ficam no diretório local de evidências; o arquivo histórico
de 20/10/2026 foi preservado. O runner foi copiado para `/tmp` alterando somente
o destino da nova evidência.

## Como reproduzir os gates

Execute na raiz do repositório, usando um projeto Compose exclusivo. Neste host,
as redes livres usadas foram as seguintes; confira conflitos em outro host:

```bash
export CLIMAPREV_BACKEND_SUBNET=10.253.92.0/24
export CLIMAPREV_LOCAL_SUBNET=10.253.93.0/24
export CLIMAPREV_FRONTEND_IP=10.253.93.10
docker compose -p climaprev-rc1-test build app
docker compose -p climaprev-rc1-test up -d --wait redis
docker compose -p climaprev-rc1-test run --rm --no-deps \
  -e REDIS_URL=redis://redis:6379/15 \
  -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" \
  app pytest -q -W error
docker compose -p climaprev-rc1-test run --rm --no-deps \
  -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" \
  app ruff check src tests --ignore EXE002
docker compose -p climaprev-rc1-test run --rm --no-deps \
  -v "$PWD/src:/app/src:ro" app mypy src
```

Durante os incrementos foi reutilizada a imagem de dependências qualificada,
com `src` e `tests` atuais montados somente leitura. Os builds de runtime de cada
fase usaram o Dockerfile original, sem modificar dependências ou locks.

```bash
docker build --load --target runtime -t climaprev-rc1-runtime:local .
docker run --rm --pids-limit=128 \
  -v "$PWD/tests/docker/check_runtime_image.py:/tmp/check_runtime_image.py:ro" \
  climaprev-rc1-runtime:local python /tmp/check_runtime_image.py
docker build --load --target build -f frontend/Dockerfile \
  -t climaprev-rc1-frontend-checks:local frontend
docker run --rm --pids-limit=256 --cpus=2 \
  climaprev-rc1-frontend-checks:local npm test -- --maxWorkers=2
docker run --rm --pids-limit=64 climaprev-rc1-frontend-checks:local npm run lint
docker run --rm --pids-limit=64 climaprev-rc1-frontend-checks:local npm run build
docker run --rm --pids-limit=64 climaprev-rc1-frontend-checks:local npm audit --audit-level=high
```

O limite explícito de processos é necessário neste host: `docker run` sem esse
parâmetro recebeu `pids.max=1`, impedindo o shell de iniciar o npm. A correção
foi restrita à bancada. Nenhum teste ou configuração de produto foi relaxado.

Para o navegador, use o [runner HTTP](../../tests/docker/check_frontend_browser.py)
e a [bancada HTTPS](../../tests/docker/decoupling/README.md). Isole o projeto com
`COMPOSE_PROJECT_NAME=climaprev-rc1-browser`. Antes de executar o runner HTTPS,
redirecione em uma cópia temporária o arquivo de evidência datado para um destino
novo; não sobrescreva o histórico. O script reinicia somente API/provedor dessa
bancada e usa somente o Redis dedicado a ela.

## Caminho operacional dos artefatos

| Etapa | Entrada e função | Saída e restrição |
| --- | --- | --- |
| Protocolo | `validate_protocol` e `partition_for`, em `experimental_protocol.py` | Envelope com checksum, partições disjuntas e critérios explícitos. |
| Calendário/coleta | `build_target_calendar`; CLI `python -m climaprev.tools.experimental_campaign --calendar ARQUIVO --ledger BANCO --output DIRETORIO` | Universo completo de alvos, SQLite e capturas imutáveis; ativação exige E1. |
| Observações/pares | `parse_observations`, `pair_capture`, `pair_calendar_captures` | Unidades, semântica, qualidade e proveniência; ausência permanece null. |
| Comparação | `compare_variable_models`, `paired_uncertainty`, `export_study_report` | Mesma amostra entre braços, cobertura, exclusões e incerteza; sem promoção automática. |
| Registro | `register_candidate` | Política, calibração, normalização, modelos, protocolo e código identificados. |
| Desenvolvimento | `select_development` | Espaço finito e regra de desempate declarados no protocolo; lê somente loaders de ajuste e validação. |
| Teste independente | `evaluate_frozen_test` | E2, hashes congelados antes/depois e população da partição de teste; não possui interface de ajuste. |
| Parecer | `record_decision`, `accepted_candidate` | Pendente, manter V1, rejeitar, inconclusivo ou promover; promoção depende dos hashes avaliados e E3. |
| Previsão preparada | `prepare_forecast` e `PreparedCandidateForecast` | Contrato `NormalizedForecast`, fontes identificadas e expiração explícita; sem coleta ou fitting na requisição. |

As funções novas de seleção/avaliação são interfaces Python opt-in. O comando
histórico existente mantém seu comportamento. O protocolo declara o espaço de
desenvolvimento por fingerprints de política, perfil, normalização e modelos;
o hash do envelope da candidata também vincula o protocolo. Essa separação
evita uma dependência circular de hashes.

O módulo `historical_experiment.py` faz parte do fingerprint legado. Snapshots
anteriores continuam íntegros, mas seu replay exige a revisão de código original
ou uma migração explícita. Recalcular hashes para ocultar mudança de algoritmo
não faz parte deste fluxo.

A temperatura horária do CSV automático INMET é registrada como média da hora
anterior; o vento horário representa os dez minutos anteriores. O pareador de
instantes só aceita medições realmente instantâneas. Equivalência científica
entre semânticas permanece uma decisão documentada do protocolo. Totais de
chuva de seis horas podem formar uma soma diária completa, mas nunca um máximo
horário fictício. D+7 sem V1 elegível mantém ganho contra V1 em null.

## Seleção explícita e retorno completo à V1

A seleção só é aplicável depois de existir um bundle real aprovado. Não use os
bundles sintéticos dos testes como autorização. O bundle JSON possui
`schema=climaprev-accepted-bundle-v1`, `protocol`, `candidate`, `evaluation`,
`decision` e `forecasts` preparados. Sua normalização deve corresponder ao
`normalization_identity()` da versão instalada. As fontes de cada previsão
possuem SHA256; os registros não certificam autenticidade externa dos dados.

1. Preserve a configuração atual e o bundle aprovado em armazenamento restrito.
2. Para uma implantação autorizada, monte o bundle somente leitura e informe
   `CLIMAPREV_CANDIDATE_BUNDLE_FILE` com seu caminho dentro do processo/container.
   O Compose atual não encaminha essa variável automaticamente: use um override
   explícito contendo a variável e o volume. Não altere o perfil de produção
   durante os ensaios locais.
3. Reinicie o processo com a configuração escolhida. `create_app` recusa
   identidades, parecer ou E3 inválidos antes de iniciar as dependências.
4. Confira uma consulta dentro do escopo preparado, os campos de qualidade,
   a política selecionada e os alertas oficiais. A expiração é verificada mesmo
   no cache e novamente antes da resposta. Escopo ausente ou expirado falha
   pelo contrato de indisponibilidade; a aplicação não troca de estratégia
   silenciosamente.
5. Para retornar à baseline, remova `CLIMAPREV_CANDIDATE_BUNDLE_FILE`, o volume
   correspondente e qualquer argumento `strategy_bundle` da fábrica da aplicação.
   Reinicie o processo. O startup recompõe Open-Meteo, `reference-v1`, a
   normalização original e `ForecastCalibration.disabled()`.
6. Confira a consulta e a política `reference-v1`. O cache da candidata possui
   identidade própria; o retorno pode reutilizar uma entrada válida da V1 sem
   reutilizar valores calibrados da candidata. Não é necessário limpar Redis.

O ensaio automatizado executou baseline → candidata → cache da candidata →
retorno à baseline. A fixture retorna 40 °C na V1 e 30 °C com o perfil sintético;
a repetição mantém 30 °C e o retorno restaura 40 °C e a política `reference-v1`.
Foram verificadas duas identidades de cache, uma única chamada ao provedor
original e a restauração do perfil `disabled`. Outro caso entra e sai do lifespan
real da fábrica, conferindo o adaptador Open-Meteo no startup padrão.

Para reproduzir esse roteiro sem dados externos:

```bash
docker compose -p climaprev-rc1-test run --rm --no-deps \
  -e REDIS_URL=redis://redis:6379/15 \
  -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" \
  app pytest -q -W error tests/integration/application/test_candidate_selection.py
```

## Pendências de uso real

- Protocolo científico final e E1 para campanha real.
- Evidência suficiente e E2 para desenvolvimento e avaliação confirmatória reais.
- Parecer humano vinculado à candidata avaliada e E3 para seleção operacional.
- Artefatos meteorológicos preparados, atuais e com escopo aprovado.
- Autorização específica para push, merge, publicação ou operação em produção.

Até essas decisões, a entrega é preparação técnica testada. Não há candidata
cientificamente promovida, superioridade demonstrada ou deploy concluído.
