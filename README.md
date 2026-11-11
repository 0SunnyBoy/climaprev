# ClimaPrev

## Estado atual — 31/10/2026

[Refatoração revisada e infraestrutura D+7](docs/operacoes/refatoracao-controle-d7-2026-10-30.md): 1.207 testes backend, 61 frontend, Ruff/mypy (102 módulos), tipagem e build aprovados localmente. D+7 implementado e desativado; protocolo/calendário próprios pendentes, piloto preservado. Arquivos existentes simplificados, sem mudança de contrato OpenAPI ou precisão demonstrada da candidata.

Backend e frontend **0.1.0**, branch **develop**, monorepo com builds e execução separados. Base funcional publicada: `ffa50f11cf0a4b0e68acdd249f80d0c8f8abca15` (`ffa50f1`); esta revisão documental é posterior a essa base, sem nova release.

Janela pública **14/7** concluída: consultas de um a sete dias consecutivos entre hoje UTC e +13, inclusive. O calendário da interface e a API GET/POST aplicam os mesmos limites. A agregação meteorológica mantém o fuso da localidade. Disponibilidade pontual na segunda semana verificada; isso não comprova precisão.

Qualificação da base: **1.170 testes backend**, mypy em **99 módulos**, **60 testes frontend**, Ruff, tipagem, lint e build aprovados. [CI aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906751) e [Security gates aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906743) no SHA `ffa50f1`. Esses resultados não qualificam automaticamente commits posteriores.

**Reference-v1 permanece padrão.** A infraestrutura das duas frentes da candidate-1 está integrada: fontes/coleta/arquivos, normalização, pareamento, cobertura, comparação, incerteza, revisão instrumental, variantes fixas e relatório técnico do piloto. Não há superioridade real demonstrada, fitting concluído, seleção confirmada ou promoção.

Observações recentes das estações A201, A001 e A801 foram obtidas pela interface oficial TEMPO, com originais e proveniência preservados; a API direta retornou 204 na última verificação. Preflight diagnóstico de 30/10: 15/15 braços/pontos disponíveis para D+1, sem contar para a cota. Não generalizar esse resultado para todos os horizontes ou variáveis.

Piloto adaptativo v5 autorizado e agendado diariamente às **15h de Brasília**, janela 18:00–18:30 UTC, a partir de 31/10. Meta: **14 capturas elegíveis por estação/modelo, 210 ao todo**, sem data-limite fixa. Perdas são preservadas e repostas em novas datas futuras; sem backfill. Encerrar previsões por par ao atingir a cota e acompanhar a cauda observacional até o último D+7 real. Notebook/Codex indisponíveis podem perder slots. Estado da preparação: zero capturas do piloto; progresso posterior exige auditoria do ledger, não inferência a partir do agendamento.

O protocolo e os hashes congelados do piloto foram preservados. A ampliação pública 14/7 não acrescenta D+7 retroativamente ao controle experimental de sete datas. Novo controle ou alteração de partições requer versão metodológica explícita; reposições que invadam partições condicionais exigem replanejamento antes da análise. Sem abertura indevida de reservas, E2/E3, promoção, merge na main ou deploy.

[Contexto e relatórios](docs/contexto/README.md) · [Pendências](docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md)

O lote de refatoração/D+7 foi publicado em `b2894b3`, com [CI](https://github.com/0SunnyBoy/climaprev/actions/runs/41154650970) e [Security](https://github.com/0SunnyBoy/climaprev/actions/runs/41154650954) aprovados.

O backend também possui uma distribuição independente para integração: [ClimaPrev-API](https://github.com/0SunnyBoy/ClimaPrev-API), com [escopo e validação próprios](docs/operacoes/extracao-api-backend-2026-10-31.md). Pesquisa e frontend permanecem neste projeto.

## Documentação do projeto

- [Índice de contexto e relatórios](docs/contexto/README.md).
- [Estado atual](docs/projeto/STATE.md), [pendências](docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md) e [sequência](docs/projeto/ROADMAP.md).
- [Frente 1: dados e integrações](docs/contexto/RELATORIO-CANDIDATE-1-FRENTE-1-DADOS-E-INTEGRACOES.md) e [Frente 2: ciência e precisão](docs/contexto/RELATORIO-CANDIDATE-1-FRENTE-2-CIENCIA-E-PRECISAO.md).
- [Arquitetura](docs/arquitetura/arquitetura.md), [frontend](frontend/README.md) e [manual do piloto](docs/operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md).
- [Janela 14/7](docs/operacoes/horizonte-14-consulta-7-2026-10-30.md) e [sincronização documental](docs/projeto/SINCRONIZACAO-DOCUMENTAL-2026-10-30.md).

Relatórios datados preservam seus resultados históricos; STATE e RDP consolidam o presente.

## Executar com Docker

```bash
docker compose up --build
```

A interface fica em `http://localhost:8080/`, servida pelo Nginx. O serviço
`app` continua disponível em `http://localhost:8000/` para acesso direto à API
e para debug. No uso normal, o frontend encaminha as consultas para o backend
na rede interna do Compose.

Para acompanhar alterações de design ao salvar arquivos Vue/CSS, use o servidor
de desenvolvimento do Vite dentro do Docker:

```bash
docker compose -f docker-compose.yml -f docker-compose.design.yml up --build app frontend-dev
```

Abra `http://localhost:5173/`. Esse modo atualiza a página automaticamente e
encaminha as chamadas da API para o serviço `app`. O `docker compose up --build`
padrão continua entregando o build estático em `http://localhost:8080/`; nele,
alterações no frontend exigem rebuild.

Na cópia correta do projeto, provisionamento de homologação, inicialização do
Git e publicação da branch são etapas separadas. Não copie `.homolog/` para o
repositório: gere seus secrets e certificados localmente conforme o runbook.
Escolha cidade ou coordenadas, período de até sete dias e Celsius/Fahrenheit.
Os resultados mostram dias, qualidade, fonte/coleta, risco estimado e alertas
oficiais em seções separadas. Dados ausentes não viram zero; dados desatualizados
recebem aviso. Erros mantêm o formulário e exigem nova tentativa manual.
O campo de cidade oferece até cinco sugestões de localidade antes do envio.
Quando há risco no período, a interface destaca o dia ou os dias de maior risco
e informa as condições que motivaram a classificação. Alertas oficiais têm
prioridade no resumo, mas a avaliação heurística permanece visível para
transparência.

A consulta usa Vue 3, TypeScript estrito e assets compilados pelo Vite. Não há
fontes externas, cookies de identidade, histórico ou sessionStorage. O
`localStorage` guarda as preferências de tema claro/escuro e idioma PT-BR/EN; não
guarda localização, consultas, credenciais ou dados de previsão. A URL da
página não recebe a localização consultada. Sem JavaScript, a página informa
essa necessidade. O formato do campo de data segue o navegador; a API sempre
recebe ISO `YYYY-MM-DD`.

```bash
# Substitua DATA_UTC_ATUAL por hoje UTC em YYYY-MM-DD.
curl "http://localhost:8080/api/v1/risk?location_text=Sao%20Paulo&start_date=DATA_UTC_ATUAL&temperature_unit=celsius"
curl "http://localhost:8080/api/v1/risk?latitude=-23.5505&longitude=-46.6333&start_date=DATA_UTC_ATUAL&temperature_unit=fahrenheit"
```

O frontend envia a consulta principal como `POST /api/v1/risk`; o `GET`
continua disponível para clientes diretos e exemplos simples.

O Docker compila `frontend/` com Vite e a imagem final do Nginx entrega somente
`frontend/dist/`. O Nginx encaminha `/api/v1/risk`, `/api/v1/locations` e
`/health/` para o serviço `app`. O backend não serve mais HTML ou assets; por
isso, a porta `8000` não entrega a interface.

`location_text` ou o par `latitude`/`longitude` é obrigatório. `end_date` é
opcional e o período aceita até sete dias. `temperature_unit` aceita `celsius`
ou `fahrenheit`; só temperaturas são convertidas, não chuva, vento ou umidade.

O endpoint devolve `forecast_risk`, `risk_overview`, `official_alerts` do INMET, `data_quality`,
fonte, `request_id` e disclaimer. `official_alerts` informa `available` quando
há resposta válida do INMET e `unavailable` quando a dependência não pode ser
consultada; `risk_overview` informa quando um alerta oficial assumiu prioridade
no resumo. Erros usam
o envelope estável `{ "error": { "code", "message", "request_id" } }`.

A política heurística pode ser avaliada offline com casos históricos revisados
por meio de `climaprev.domain.risk_validation`. A calibração estatística existe
como camada opcional versionada, mas permanece desativada até haver evidência
suficiente; `reference-v1` continua sendo o fallback seguro.

Reconstrua a imagem com `docker compose build app` após alterar os módulos.
Para executar um diagnóstico histórico sem banco de dados, use o Previous Runs
da Open-Meteo (`gfs_global`) e a reanálise Historical Weather (`era5`). A v1
aplicada à reanálise fornece um alvo heurístico fixo, sem representar impactos
observados. Salve as entradas para reproduzir a avaliação sem nova coleta:

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

No PowerShell, use:

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

O processo é limitado a 31 dias por coleta e aceita antecedência de 1 a 7
dias. Para o piloto diagnóstico, repita com antecedências 3 e 7 em arquivos
próprios. A disponibilidade de modelo, variável e período precisa ser
verificada. Cobertura mínima de 100% da variável de cada evento exclui
casos incompletos, em vez de substituir ausências por zero. O relatório
inclui casos, exclusões e métricas; denominador zero resulta em `null` nas
métricas experimentais. Unidades explícitas são verificadas. Os hashes dos
snapshots permitem verificar consistência, sem comprovar autenticidade da
fonte; hashes do pipeline impedem replay silencioso com algoritmos alterados.

Reprodução sem rede:

```powershell
docker compose run --rm --mount "type=bind,source=$reports,target=/app/.historical-reports" app `
  python -m climaprev.tools.validate_historical `
  --input /app/.historical-reports/belem-2025-01-lead-1-input.json `
  --output /app/.historical-reports/belem-lead-1-replay.json
```

Comparação da baseline sobre entradas salvas:

```powershell
docker compose run --rm --mount "type=bind,source=$reports,target=/app/.historical-reports" app `
  python -m climaprev.tools.compare_historical `
  --input /app/.historical-reports/belem-2025-01-lead-1-input.json `
  --protocol docs/planejamento/reference-candidate-1/protocolo-piloto.json `
  --partition diagnostic --output /app/.historical-reports/belem-diagnostic.json
```

O comparador aceita vários arquivos após `--input`, `--candidate` para regras
experimentais e `--calibration` para um perfil experimental. Assim gera R0
(v1 original), A (candidata), B (v1 calibrada) e AB (combinação), quando as
respectivas configurações forem fornecidas. Nenhuma configuração é aprovada
ou ativada automaticamente. O [protocolo piloto](docs/planejamento/reference-candidate-1/protocolo-piloto.md)
contém splits apenas propostos; dados do diagnóstico não constituem teste final
reservado. Metas científicas, suficiência amostral e revisor continuam pendentes.
Veja formatos de configuração, partições e limites em
[validação e calibração](docs/arquitetura/validacao-e-calibracao.md).

Para executar diretamente em um ambiente Python Windows já provisionado,
instale `python -m pip install --require-hashes -r requirements-windows-dev.lock`.
Esse complemento mantém os pins de desenvolvimento e acrescenta dependências
Windows (`colorama` e base IANA `tzdata`), sem substituir os locks Linux.
Execute a partir da raiz com `$env:PYTHONPATH = (Resolve-Path src).Path` para
disponibilizar os módulos locais.

Os códigos usuais são 422 (entrada), 404 (local não encontrado), 429 (limite),
502 (dados inválidos ou requisição rejeitada pelo provedor) e 503 (dependência indisponível).

O 429 do provedor retorna `503 WEATHER_PROVIDER_UNAVAILABLE`, sem retry automático
nessa operação e com fallback apenas dentro do TTL. Outros 4xx externos retornam
`502 WEATHER_PROVIDER_REJECTED`, sem retry nem fallback. Rede, timeout e 5xx têm
até duas tentativas adicionais. Mensagens externas não aparecem na resposta.

Redis reduz chamadas repetidas: previsões frescas duram 10 minutos e podem ser
servidas como `stale` até 15 minutos quando o provedor falha. O limite padrão é
60 requisições/minuto por cliente, com burst de 10. Fontes meteorológicas:
[Open-Meteo Forecast](https://open-meteo.com/),
[Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) e
[INMET — avisos ativos](https://apiprevmet3.inmet.gov.br/avisos/ativos).

## Testes

Todos os testes executam dentro de Docker:

```bash
docker compose build
docker compose run --rm app pytest -q -W error
docker compose run --rm app ruff check src tests --ignore EXE002
docker compose run --rm app mypy src
```

Os gates do frontend são executados na etapa Node da imagem e podem ser
reproduzidos dentro de `frontend/` com `npm ci`, `npm run lint`,
`npm run typecheck`, `npm run test` e `npm run build`. A imagem final não
contém `node_modules` nem ferramentas de desenvolvimento.

O roteiro [Browser B01–B10](docs/planejamento/evolucao-climaprev/evidence/browser-tests.md)
registra testes reais em Chrome, cenários controlados, teclado, capturas 360/1280
e validação HTTPS em perfil temporário com CA explícita. Scripts são extraídos
para `/tmp`; não há instalação npm requerida pelo aplicativo.

O smoke de carga é curto e não representa a meta de capacidade. Cada usuário
do Locust é limitado por taxa de chegada a 1 requisição/s; portanto, 100
usuários representam aproximadamente 100 requisições/s após o aquecimento:

```bash
docker compose --profile load build load provider-mock app-load
docker compose --profile load up -d --wait provider-mock app-load
docker compose --profile load run --rm --no-deps load locust -f tests/load/locustfile.py --host http://app-load:8000 --headless --users 2 --spawn-rate 2 --run-time 10s --only-summary
```

O perfil `load` usa o app real, Redis real e um provedor Open-Meteo compatível,
determinístico e interno ao Compose. O serviço `app` padrão continua apontando
para Open-Meteo público. Selecione `CLIMAPREV_LOAD_SCENARIO` antes de subir o
perfil: `warm_cache` usa e prima uma chave fixa, `cold_cache` usa uma chave de
localização única por requisição, `lock_contention` reutiliza uma chave entre
usuários concorrentes, `slow_upstream` atrasa o provider mock e `redis_latency`
atrasa operações Redis apenas no `app-load`. O status 429 é
sempre contado como falha. O mock de carga usa orçamento externo alto, ainda
ativo: capacidade/reposição de 100000 por 60 s. Ajuste com
`CLIMAPREV_LOAD_PROVIDER_BUDGET_CAPACITY`, `CLIMAPREV_LOAD_PROVIDER_BUDGET_REFILL`
e `CLIMAPREV_LOAD_PROVIDER_BUDGET_WINDOW_SECONDS`. Isso se aplica somente ao
`app-load` apontado ao mock; não amplia a cota do Open-Meteo público. Um 503
causado por orçamento esgotado não mede a capacidade de processamento do backend.

O cenário adicional `lock_contention` reutiliza uma chave única entre usuários
concorrentes para medir a contenção do lock distribuído.

Veja [operações](docs/operacoes/operations.md) para configuração, métricas e baseline.

## Integração contínua

O workflow [CI](.github/workflows/ci.yml) executa automaticamente em cada
`push`, Pull Request ou execução manual pelo GitHub. Ele constrói a imagem,
executa a suíte de testes, Ruff, mypy, valida o Nginx e faz um smoke test do
frontend e da saúde da API. A CI não faz deploy; apenas valida o estado do
repositório em um runner temporário. O smoke test descobre os assets hashados
no HTML gerado pelo Vite; ele não depende de `/assets/styles.css`.

A configuração local atual também executa ESLint, Vitest e `npm audit
--audit-level=high` em uma imagem derivada do estágio de build do frontend.
Os checks devem ser executados para cada lote enviado; resultados locais
não representam uma nova execução remota já aprovada.

## Estado da branch

O desenvolvimento ocorre na branch `develop`; a branch `main` recebe somente
alterações estáveis aprovadas para publicação. O checkout atual
`climaprev-develop` está vinculado ao histórico Git original. O código funcional
14/7 foi publicado em `ffa50f1`, com CI e Security aprovados; a reorganização
documental foi publicada em `355a158`, também qualificada por CI/Security.
O incremento de refatoração/D+7 exige seus próprios checks na publicação. A pasta `.homolog/` permanece local,
ignorada pelo Git, e deve ser provisionada separadamente para validar a
homologação.


## Homologação com TLS

O perfil separado usa runtime não root, Redis autenticado, entrada TLS local
e coleta sanitizada com retenção máxima de sete dias. Veja o procedimento e
as limitações de rede em [homologação local](docs/operacoes/homologacao.md). A CA é
confiada explicitamente; não há publicação externa. Nesse perfil os logs ficam
no volume do coletor, sem stdout persistido pelo engine; o documento mostra
como lê-los e diagnosticar os serviços.

## Preparação da candidata

Estado vigente nas [duas frentes](docs/contexto/README.md) e no [RDP](docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md). Piloto v5 agendado até a cota; os diagnósticos de 19/10 abaixo são históricos e não representam a cobertura atual ou comprovação de ganho.

Veja a [execução técnica de 19/10/2026](docs/planejamento/reference-candidate-1/execucao-2026-10-19.md)
para os cruzamentos observacionais ampliados, a auditoria da referência e o
estado da infraestrutura de incerteza. A reference-v1 permanece ativa e a
preparação técnica não equivale a aprovação científica ou promoção.

A [continuação da reconciliação e do suporte observacional](docs/planejamento/reference-candidate-1/reconciliacao-e-suporte-2026-10-19.md)
explica a equivalência dos 417,0 mm do boletim com o dia encerrado às 12 UTC e
registra as contagens de eventos nas estações, preservando os alvos civis anteriores.

O [diagnóstico da baseline e a proposta de critérios](docs/planejamento/reference-candidate-1/baseline-e-criterios-propostos-2026-10-19.md)
apresentam métricas por evento e estrato, além dos bloqueios antes de qualquer
ajuste. Esses resultados experimentais não equivalem a reprodução integral da API.

O [pareamento de máximos horários](docs/planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md)
completa a baseline diagnóstica de cinco eventos, preservando os pais e as mesmas
datas elegíveis. A nova versão da baseline e do preflight está referenciada nesse documento.
# Execução independente da interface e API

Frontend e backend possuem builds e execução separados. Veja [guia de desacoplamento](docs/arquitetura/desacoplamento-2026-10-20.md), [frontend](frontend/README.md) e [RDP vigente](docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md). O modo integrado por proxy permanece disponível.
