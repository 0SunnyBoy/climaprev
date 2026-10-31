# Tarefas — evolução do Clima Prev

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

> Este arquivo preserva o plano e as evidências do ciclo original. A
> implementação atual do frontend foi posteriormente migrada para Vue 3,
> TypeScript e Vite em `frontend/src/`. Referências históricas a
> `frontend/api.js`, `frontend/app.js`, `frontend/result.js` e
> `frontend/styles.css` descrevem o estado anterior das tarefas T21–T25; não
> são caminhos ativos do runtime atual.

> Este arquivo preserva o plano e as referências do ciclo base. As tarefas
> T21–T25 registram a implementação vanilla original; o rework atual foi
> concluído em Vue 3 + TypeScript e está catalogado em
> `docs/frontend/Frontend-Rework.md`.

**Estado:** Ciclo base concluído; incrementos P0–P2.6 concluídos; revisão independente pendente.
**Spec:** [spec.md](spec.md). **Design:** [design.md](design.md).
**Progresso de implementação:** 25/25 tarefas base concluídas, com incrementos posteriores registrados em `docs/projeto/ImplementationsAndRefactoring.md`.

## Execution Protocol

A execução local e a coordenação de agentes foram solicitadas pelo usuário
em 2026-09-13. Executar com a skill `tlc-spec-driven`, respeitando as
instruções da sessão, a spec e os critérios abaixo. Revisar premissas antes do bloco afetado.
Cada tarefa entrega um comportamento e seus testes; não adiar testes de uma
alteração para uma tarefa posterior. Não alterar assertions válidas para
ocultar regressões. Registrar desvios e resultados reais.

Cada tarefa foi concluída com commit atômico após seu gate. Não incluir arquivos de outras tarefas
ou alterações locais anteriores por engano. Commits locais atômicos fazem parte desta execução. Push e publicação
externa não fazem parte do pedido.

Ao finalizar a implementação, realizar a verificação independente prevista
pela skill, com evidência por requisito e teste de discriminação em cópia
isolada. Um documento estruturalmente válido não é um sistema homologado.

## Test Coverage Matrix

Gerada a partir de README, pyproject.toml e amostras existentes em
`tests/unit/api`, `tests/unit/domain`, `tests/integration/api`,
`tests/integration/providers` e `tests/integration/redis`.
Não foi encontrado AGENTS.md ou CONTRIBUTING.md no repositório.

| Code Layer             | Required Test Type                     | Coverage Expectation                                                    | Location Pattern                        | Run Command |
| ---------------------- | -------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------- | ----------- |
| Domínio e configuração | unitário                               | Critérios da spec e todos os limites/casos inválidos relevantes.        | `tests/unit/`                           | Quick       |
| API/aplicação/provedor | integração                             | Sucesso, erro e fronteiras; provider controlado.                        | `tests/integration/`, `tests/contract/` | Full        |
| Redis/cache/lock/cota  | integração                             | Redis real, concorrência, expiração e indisponibilidade.                | `tests/integration/redis/`              | Full        |
| Imagem e dependências  | integração Docker / build reproduzível | Conteúdo, usuário, dependências, dois builds e preservação do alvo dev. | `tests/docker/`                         | Build       |
| Entrada e isolamento   | integração Docker                      | Rota pública/interna, TLS, ACL, segredos e logs sanitizados.            | `tests/docker/` e evidência local       | Homolog     |
| Frontend nativo        | navegador e visual                     | Formulário, estado, rede, apresentação e teclado conforme B01–B10.      | Roteiro abaixo; fixtures controladas    | Browser     |

Os testes de frontend são verificações funcionais no navegador; não existe
runner JS/npm neste projeto e não se presume sua instalação. O executor pode
automatizar o roteiro com ferramentas de navegador disponíveis, preservando
os mesmos resultados esperados e registrando evidência por caso.

## Gate Check Commands

Executar os comandos de aplicação dentro de Docker, na raiz do Clima Prev.
Preparação já adotada pelo projeto: `docker compose build`.

| Gate Level | When to Use                                     | Command                                                                                                                              |
| ---------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Quick      | Testes unitários da alteração                   | `docker compose run --rm app pytest -q -W error tests/unit`                                                                          |
| Full       | Integração, contrato ou fronteira de componente | `docker compose run --rm app pytest -q -W error`                                                                                     |
| Build      | Imagem, dependências e fechamento de fase       | `docker compose build`, seguido de Full, `docker compose run --rm app ruff check src tests --ignore EXE002` e `docker compose run --rm app mypy src` |
| Homolog    | Após T19/T20 criarem a stack                    | Comandos abaixo e provas de rede/TLS/Redis descritas no aceite.                                                              |
| Browser    | Interface funcional                             | Executar B01–B10 aplicáveis e registrar entrada, ação, saída esperada/observada.                                                     |

Comandos de homologação implementados em T19/T20, com secrets e CA já provisionados:

```bash
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml config --quiet
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml build
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml up -d
```

Secrets e CA local devem ser provisionados conforme T19/T20 antes do up.
`config --quiet` evita imprimir configuração expandida com dados sensíveis.
A passagem dos comandos não substitui as provas de acesso negado/TLS/logs.
Parar apenas a stack temporária criada pelo executor; não remover volumes
ou serviços preexistentes. O gate Build deve continuar funcionando após T18
selecionar explicitamente o alvo dev no Compose de testes.

As contagens por tarefa abaixo são **mínimos de cenários planejados**, não
resultados executados nem contagem histórica da suíte. Registrar a coleção
atual antes da alteração e preservar os testes existentes pertinentes.

## Execution Plan

Cinco fases, executadas em ordem. Para uma retomada simples, cada tarefa
depende da anterior; a dependência inclui a passagem do gate anterior.
O encadeamento representa a ordem de integração, não exige novas dependências
entre módulos do código. Ao final de cada fase, executar Build.

```text
T1 -> T2 -> T3 -> T4 -> T5
T5 -> T6 -> T7 -> T8 -> T9 -> T10
T10 -> T11 -> T12 -> T13 -> T14 -> T15
T15 -> T16 -> T17 -> T18 -> T19 -> T20
T20 -> T21 -> T22 -> T23 -> T24 -> T25
```

## Task Breakdown

`Where` indica o componente principal. Adequações de contratos, wiring,
fixtures e testes estritamente necessárias ao mesmo comportamento integram
a mesma tarefa, explicitadas em What/Reuses; não são trabalho implícito em
outro módulo. Não criar arquivos vazios para antecipar tarefas.

### Phase 1: Dados e identidade de previsão

#### T1: Corrigir o fuso efetivo da previsão

**What**: Normalizar o fuso do payload e projetá-lo na resposta do serviço, também no cache hit.
**Where**: `src/climaprev/infrastructure/providers/open_meteo.py`
**Depends on**: None
**Reuses**: Adaptador e projeção de local existentes.
**Requirement**: DAT-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Texto, coordenadas, cache hit e timezone inválido; conferir o fuso esperado no JSON público.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos DAT-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(forecast): preserve effective forecast timezone`.

#### T2: Validar valores meteorológicos

**What**: Rejeitar valores fora do contrato antes de avaliação ou cache.
**Where**: `src/climaprev/infrastructure/providers/open_meteo.py`
**Depends on**: T1
**Reuses**: Helpers numéricos do adaptador.
**Requirement**: DAT-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 12 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: NaN, infinitos, percentuais -1/101 e limites 0/100, chuva/vento negativos, mínima maior que máxima e null válido.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos DAT-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(provider): validate meteorological value bounds`.

#### T3: Entregar completude dos dados na API

**What**: Calcular completude e cobertura civil horária e ligar o resultado ao DTO e ao schema HTTP no mesmo incremento.
**Where**: `src/climaprev/domain/data_quality.py`
**Depends on**: T2
**Reuses**: Modelos de domínio, missing_fields e serialização da rota.
**Requirement**: DAT-03
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 8 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: complete/partial/unavailable, zero legítimo, nulos, amostra ausente, dia de 23 h, dia de 25 h e horário extra inválido.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos DAT-03 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(quality): expose forecast data completeness`.

#### T4: Calcular média diária de temperatura

**What**: Preencher a média com amostras horárias não nulas e preservar conversão na saída.
**Where**: `src/climaprev/infrastructure/providers/open_meteo.py`
**Depends on**: T3
**Reuses**: Agregadores horários e conversor de unidade.
**Requirement**: DAT-04
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Média conhecida em Celsius, conversão Fahrenheit, série parcial e nenhuma amostra.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos DAT-04 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(forecast): calculate daily mean temperature`.

#### T5: Corrigir identidade e versão do cache

**What**: Criar chave forecast:v2 determinística sem arredondar coordenadas e validar conteúdo por identidade meteorológica.
**Where**: `src/climaprev/application/services/forecast_query.py`
**Depends on**: T4
**Reuses**: Chaves, serialização e composição de local do serviço.
**Requirement**: CON-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 5 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Pontos que colidiam, mesmo ponto com nomes diferentes, outro período, outro destino e Celsius/Fahrenheit compartilhando dado canônico.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos CON-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(cache): separate forecast identity from display metadata`.

### Phase 2: Cache, falhas e configuração numérica

#### T6: Revalidar expiração antes de fallback

**What**: Transportar expires_at no contrato CacheEntry e verificar validade imediatamente antes de entregar stale.
**Where**: `src/climaprev/application/services/forecast_query.py`
**Depends on**: T5
**Reuses**: Porta/adaptador de cache, serviço e fakes existentes.
**Requirement**: RES-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 6 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: 599/600/899/900 segundos e expiração após espera por lock ou retry; leitura não renova TTL.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos RES-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(cache): enforce expiry at fallback delivery`.

#### T7: Tratar envelope Redis corrompido

**What**: Validar envelope e tratar corrupção como miss com contador fixo, preservando 503 para falha de conexão.
**Where**: `src/climaprev/infrastructure/cache/redis_cache.py`
**Depends on**: T6
**Reuses**: RedisCache e coletor de métricas.
**Requirement**: RES-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 6 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: JSON inválido, campos ausentes, tipos incorretos, datas não finitas, ordem temporal inválida e Redis desconectado.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos RES-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(cache): reject malformed cache envelopes safely`.

#### T8: Mapear falhas do provedor

**What**: Separar exceções no contrato de aplicação e mapear 429, outros 4xx e falhas transitórias na API.
**Where**: `src/climaprev/infrastructure/http/client.py`
**Depends on**: T7
**Reuses**: Retry, backoff e handlers sanitizados existentes.
**Requirement**: RES-03
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 7 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: 429 sem retry, 400, 401, 404, 5xx com até três tentativas, timeout e payload inválido sem retry; nunca revelar body externo.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos RES-03 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(provider): distinguish rejected and unavailable requests`.

#### T9: Encerrar atualização sem propriedade

**What**: Cancelar atualização quando heartbeat perder o lock e preservar erro principal durante cleanup.
**Where**: `src/climaprev/application/services/forecast_query.py`
**Depends on**: T8
**Reuses**: Token de lock, heartbeat e cancelamento existentes.
**Requirement**: RES-04
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Perda de lock, falha de release após erro principal, cancelamento do cliente e token alheio preservado.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos RES-04 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(lock): stop refresh after ownership loss`.

#### T10: Validar intervalos de configuração

**What**: Rejeitar valores numéricos inválidos antes do lifespan, preservando clamp superior de retries.
**Where**: `src/climaprev/config.py`
**Depends on**: T9
**Reuses**: Settings e testes de configuração existentes.
**Requirement**: CFG-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário; mínimo de 10 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Quick, conforme Gate Check Commands.
**Casos de verificação**: Zero/negativos para limites e timeouts, não finitos, retries -1/0/2/3 e configuração padrão.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos CFG-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Quick aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(config): validate runtime numeric limits`.

### Phase 3: Fronteiras e consumo externo

#### T11: Validar destinos meteorológicos

**What**: Validar esquema, host, porta, credenciais e fragmento das URLs de produção e manter exceção load explícita.
**Where**: `src/climaprev/config.py`
**Depends on**: T10
**Reuses**: Settings e URLs dos adaptadores existentes.
**Requirement**: CFG-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 8 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: HTTPS autorizado, host não permitido, HTTP de produção, userinfo, fragmento, porta indevida, mock load e mocks de testes.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos CFG-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(config): restrict production provider destinations`.

**Evidência:** [T11](evidence/t11.md).

#### T12: Preservar limite por cliente e fronteira de proxy

**What**: Verificar o contrato da cadeia encaminhada e integrar somente correções necessárias ao cenário de entrada adotado.
**Where**: `src/climaprev/api/deps.py`
**Depends on**: T11
**Reuses**: client_identity, limiter e testes de spoofing existentes.
**Requirement**: SEC-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 6 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Peer não confiável, cadeia válida, prefixo forjado, cadeia malformada, 21 entradas e cota individual com Retry-After.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos SEC-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `test(security): verify proxy and client quota boundaries`.

**Evidência:** [T12](evidence/t12.md).

#### T13: Sanitizar registros de consulta

**What**: Garantir metadados permitidos nos logs e preparar configuração de runtime sem access log bruto.
**Where**: `src/climaprev/api/observability.py`
**Depends on**: T12
**Reuses**: Logger JSON do app e request ID validado.
**Requirement**: SEC-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Texto de localização, IP, token e payload sentinela ausentes em logs; ID, status e duração presentes.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos SEC-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(logging): keep request metadata free of sensitive input`.

**Evidência:** [T13](evidence/t13.md).

#### T14: Limitar chamadas externas globalmente

**What**: Criar decisão Redis atômica e ligá-la imediatamente antes de cada envio HTTP, inclusive retries e geocodificação.
**Where**: `src/climaprev/infrastructure/rate_limit/provider_budget.py`
**Depends on**: T13
**Reuses**: Redis, token bucket e cliente HTTP existentes.
**Requirement**: SEC-04
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 5 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Capacidade 2 com 10 chamadas concorrentes, reposição, cache hit sem gasto, retry contado e Redis indisponível sem bypass.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos SEC-04 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(rate-limit): enforce shared provider request budget`.

**Evidência:** [T14](evidence/t14.md).

#### T15: Limitar cardinalidade de rotas

**What**: Usar template da rota resolvida e unmatched para caminhos sem rota.
**Where**: `src/climaprev/api/observability.py`
**Depends on**: T14
**Reuses**: RequestMetrics e middleware atuais.
**Requirement**: OBS-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: unitário + integração; mínimo de 3 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Mil URLs desconhecidas produzem um rótulo unmatched; rotas conhecidas permanecem separadas; nenhuma query/IP em dimensões.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos OBS-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `fix(metrics): bound request route cardinality`.

### Phase 4: Operação e homologação

**Evidência:** [T15](evidence/t15.md).

#### T16: Expor snapshot interno por processo

**What**: Criar rota interna JSON com identidade e início do processo e registrá-la na aplicação.
**Where**: `src/climaprev/api/routes/metrics.py`
**Depends on**: T15
**Reuses**: RequestMetrics.snapshot e composição FastAPI.
**Requirement**: OBS-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração; mínimo de 3 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full, conforme Gate Check Commands.
**Casos de verificação**: Snapshot com campos esperados, identidade de processo e ausência de entrada/segredos; bloqueio externo será verificado em T20.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos OBS-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(metrics): expose internal process snapshot`.

**Evidência:** [T16](evidence/t16.md).

#### T17: Registrar dependências de produção

**What**: Gerar lock com versões transitivas e hashes a partir de resolução validada e documentar sua atualização.
**Where**: `requirements.lock`
**Depends on**: T16
**Reuses**: pyproject.toml como declaração de dependências diretas.
**Requirement**: OPS-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: build reproduzível; mínimo de 2 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Build, conforme Gate Check Commands.
**Casos de verificação**: Duas instalações limpas selecionam mesmas versões; arquivo não contém credenciais ou caminhos locais.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos OPS-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Build aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `build(deps): lock production dependency resolution`.


**Evidência:** [T17](evidence/t17.md).

#### T18: Separar imagem runtime e dev

**What**: Criar runtime não root e alvo dev; ajustar seleção do alvo no harness para manter os testes executáveis.
**Where**: `Dockerfile`
**Depends on**: T17
**Reuses**: Dockerfile e Compose locais, sem alterar o conteúdo de alterações alheias.
**Requirement**: SEC-03, OPS-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração Docker; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Build, conforme Gate Check Commands.
**Casos de verificação**: UID não zero; runtime sem tests/dev/.env; dev executa pytest/Ruff/mypy; pacote e assets planejados podem ser copiados.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos SEC-03, OPS-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Build aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `build(container): separate production and development images`.


**Evidência:** [T18](evidence/t18.md).

#### T19: Isolar Redis na homologação

**What**: Criar stack local separada com Redis autenticado, credenciais externas ao Git e sem portas diretas de API/Redis ao usuário.
**Where**: `docker-compose.homolog.yml`
**Depends on**: T18
**Reuses**: Serviços de desenvolvimento e health checks existentes.
**Requirement**: OPS-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração Docker; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Homolog, conforme Gate Check Commands.
**Casos de verificação**: Autenticação válida/inválida, ausência de porta Redis no host, API interna e mock/load sem entrada de usuário.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos OPS-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Homolog aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `build(homolog): isolate application and redis services`.


**Evidência:** [T19](evidence/t19.md).

#### T20: Configurar entrada TLS e coleta sanitizada

**What**: Configurar entrada de homologação com TLS local, deny das rotas internas, proxy confiável e rotação de logs.
**Where**: `docker/homolog/entrada`
**Depends on**: T19
**Reuses**: Stack de T19, contrato de proxies e logs do app.
**Requirement**: OPS-01, OBS-02, SEC-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração Docker; mínimo de 6 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Homolog, conforme Gate Check Commands.
**Casos de verificação**: TLS com CA confiável, /internal/metrics externo 404 e interno 200, query/IP ausentes dos logs e retenção de sete dias verificada.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos OPS-01, OBS-02, SEC-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Homolog aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `build(homolog): protect traffic entry and operational logs`.

### Phase 5: Interface de consulta


**Evidência:** [T20](evidence/t20.md).

#### T21: Entregar formulário e rota da interface

**What**: Criar formulário semântico e servir página/assets na mesma origem, incluindo empacotamento e registro de rota.
**Where**: `frontend/index.html`
**Depends on**: T20
**Reuses**: FastAPI e contrato do schema de consulta.
**Requirement**: UI-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: integração + navegador; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Full + Browser, conforme Gate Check Commands.
**Casos de verificação**: GET / e assets válidos; /api e /health preservados; alternância cidade/coordenadas; envio sem campos extras.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos UI-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Full + Browser aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(web): serve climate query form`.

**Evidência:** [T21](evidence/t21.md).

#### T22: Implementar cliente HTTP da interface

**What**: Serializar parâmetros e normalizar envelope de sucesso/erro sem armazenar dados pessoais.
**Where**: `frontend/api.js`
**Depends on**: T21
**Reuses**: Fetch nativo e contrato público da API.
**Requirement**: UI-01
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: navegador; mínimo de 5 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Browser, conforme Gate Check Commands.
**Casos de verificação**: Cidade, coordenadas, unidade, erro JSON e resposta malformada; inspecionar parâmetros enviados.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos UI-01 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Browser aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(web): add weather API client`.

**Evidência:** [T22](evidence/t22.md).

#### T23: Apresentar previsão e qualidade

**What**: Renderizar resultado com fonte, período, qualidade, stale, aviso e alertas separados, usando texto seguro.
**Where**: `frontend/result.js`
**Depends on**: T22
**Reuses**: Projeção pública e regras normativas de completude.
**Requirement**: UI-02
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: navegador; mínimo de 7 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Browser, conforme Gate Check Commands.
**Casos de verificação**: Complete, partial, unavailable, stale, null, estados de alertas e texto com marcação inerte sem executar HTML.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos UI-02 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Browser aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(web): present forecast quality and risk context`.

**Evidência:** [T23](evidence/t23.md).

#### T24: Controlar estados e consultas concorrentes

**What**: Coordenar loading/sucesso/erro, cancelar consulta substituída e respeitar prazo de 429.
**Where**: `frontend/app.js`
**Depends on**: T23
**Reuses**: Cliente de T22 e apresentação de T23.
**Requirement**: UI-03
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: navegador; mínimo de 6 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Browser, conforme Gate Check Commands.
**Casos de verificação**: Resposta antiga atrasada, cancelamento, 422/404, 429 válido/inválido, 502/503/rede e falha inesperada; nenhum resultado antigo rotulado como atual.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos UI-03 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Browser aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(web): handle query lifecycle and recovery`.

**Evidência:** [T24](evidence/t24.md).

#### T25: Concluir navegação e layout responsivo

**What**: Ajustar foco, layout, mensagens anunciáveis e interação por teclado nos estados do formulário.
**Where**: `frontend/styles.css`
**Depends on**: T24
**Reuses**: HTML semântico e controlador da interface.
**Requirement**: UI-04
**Tools**: leitura/edição local, Docker e pytest; skill `coding-guidelines` para código, navegador quando aplicável.
**Tests**: navegador + visual; mínimo de 4 cenários pertinentes à tarefa, além da regressão existente.
**Gate**: Browser, conforme Gate Check Commands.
**Casos de verificação**: Fluxo só por teclado, foco visível, mensagens em região de status e viewport 360/1280 px sem overflow horizontal.

**Done when**:

- [x] Parte atribuída nesta tarefa aos requisitos UI-04 e ao design entregue sem ampliar o escopo; requisito compartilhado só é verificado após todas as suas tarefas.
- [x] Casos acima verificados com evidência e gate Browser aprovado.
- [x] Status, testes executados e desvios registrados antes de encerrar a tarefa.

**Commit futuro**: `feat(web): improve responsive and keyboard query access`.

**Evidência:** [T25](evidence/t25.md).

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status         |
| ---- | ---------- | ------------- | -------------- |
| T1   | None       | Sem entrada   | Correspondente |
| T2   | T1         | T1 → T2       | Correspondente |
| T3   | T2         | T2 → T3       | Correspondente |
| T4   | T3         | T3 → T4       | Correspondente |
| T5   | T4         | T4 → T5       | Correspondente |
| T6   | T5         | T5 → T6       | Correspondente |
| T7   | T6         | T6 → T7       | Correspondente |
| T8   | T7         | T7 → T8       | Correspondente |
| T9   | T8         | T8 → T9       | Correspondente |
| T10  | T9         | T9 → T10      | Correspondente |
| T11  | T10        | T10 → T11     | Correspondente |
| T12  | T11        | T11 → T12     | Correspondente |
| T13  | T12        | T12 → T13     | Correspondente |
| T14  | T13        | T13 → T14     | Correspondente |
| T15  | T14        | T14 → T15     | Correspondente |
| T16  | T15        | T15 → T16     | Correspondente |
| T17  | T16        | T16 → T17     | Correspondente |
| T18  | T17        | T17 → T18     | Correspondente |
| T19  | T18        | T18 → T19     | Correspondente |
| T20  | T19        | T19 → T20     | Correspondente |
| T21  | T20        | T20 → T21     | Correspondente |
| T22  | T21        | T21 → T22     | Correspondente |
| T23  | T22        | T22 → T23     | Correspondente |
| T24  | T23        | T23 → T24     | Correspondente |
| T25  | T24        | T24 → T25     | Correspondente |

## Test Co-location Validation

| Task | Camada / resultado                                | Matrix Requires        | Task Says                                | Status         |
| ---- | ------------------------------------------------- | ---------------------- | ---------------------------------------- | -------------- |
| T1   | Corrigir o fuso efetivo da previsão               | integração             | integração na própria tarefa             | Correspondente |
| T2   | Validar valores meteorológicos                    | integração             | integração na própria tarefa             | Correspondente |
| T3   | Entregar completude dos dados na API              | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T4   | Calcular média diária de temperatura              | integração             | integração na própria tarefa             | Correspondente |
| T5   | Corrigir identidade e versão do cache             | integração             | integração na própria tarefa             | Correspondente |
| T6   | Revalidar expiração antes de fallback             | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T7   | Tratar envelope Redis corrompido                  | integração             | integração na própria tarefa             | Correspondente |
| T8   | Mapear falhas do provedor                         | integração             | integração na própria tarefa             | Correspondente |
| T9   | Encerrar atualização sem propriedade              | integração             | integração na própria tarefa             | Correspondente |
| T10  | Validar intervalos de configuração                | unitário               | unitário na própria tarefa               | Correspondente |
| T11  | Validar destinos meteorológicos                   | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T12  | Preservar limite por cliente e fronteira de proxy | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T13  | Sanitizar registros de consulta                   | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T14  | Limitar chamadas externas globalmente             | integração             | integração na própria tarefa             | Correspondente |
| T15  | Limitar cardinalidade de rotas                    | unitário + integração  | unitário + integração na própria tarefa  | Correspondente |
| T16  | Expor snapshot interno por processo               | integração             | integração na própria tarefa             | Correspondente |
| T17  | Registrar dependências de produção                | build reproduzível     | build reproduzível na própria tarefa     | Correspondente |
| T18  | Separar imagem runtime e dev                      | integração Docker      | integração Docker na própria tarefa      | Correspondente |
| T19  | Isolar Redis na homologação                       | integração Docker      | integração Docker na própria tarefa      | Correspondente |
| T20  | Configurar entrada TLS e coleta sanitizada        | integração Docker      | integração Docker na própria tarefa      | Correspondente |
| T21  | Entregar formulário e rota da interface           | integração + navegador | integração + navegador na própria tarefa | Correspondente |
| T22  | Implementar cliente HTTP da interface             | navegador              | navegador na própria tarefa              | Correspondente |
| T23  | Apresentar previsão e qualidade                   | navegador              | navegador na própria tarefa              | Correspondente |
| T24  | Controlar estados e consultas concorrentes        | navegador              | navegador na própria tarefa              | Correspondente |
| T25  | Concluir navegação e layout responsivo            | navegador + visual     | navegador + visual na própria tarefa     | Correspondente |

## Roteiro Browser

Usar dados sintéticos locais; o backend não consulta serviços oficiais de
alertas. Cada item exige evidência do resultado observado, não apenas um
screenshot da página inicial.

| Caso | Ação e resultado esperado                                                                                          |
| ---- | ------------------------------------------------------------------------------------------------------------------ |
| B01  | Consultar cidade e depois coordenadas; rede contém somente campos contratados.                                     |
| B02  | Período >7 dias, coordenada sem par e texto vazio impedem envio ou exibem 422 com correção.                        |
| B03  | Comparar Celsius/Fahrenheit: somente temperatura muda de unidade.                                                  |
| B04  | Resultado completo mostra fonte/coleta/local/fuso/datas/aviso e unidades.                                          |
| B05  | Partial, unavailable, null e stale recebem mensagens explícitas; sem entradas não se apresenta low como conclusão. |
| B06  | Alertas not_configured/unavailable/available vazios têm mensagens distintas.                                       |
| B07  | 404, 422, 502, 503, rede, 500 e JSON malformado mostram recuperação sem apagar contexto do formulário.             |
| B08  | 429 impede nova tentativa até Retry-After; inválido usa 60 s; não faz retry automático.                            |
| B09  | Consulta B termina antes de A: resultado final permanece B; texto com marcação não executa HTML.                   |
| B10  | Percorrer tudo por teclado em 360 px e 1280 px; rótulos, foco, status anunciável e sem overflow da página.         |

## Backlog condicionado após este ciclo

Os itens seguintes não fazem parte das 25 tarefas de implementação acima.
Não estão esquecidos nem prontos para desenvolvimento sem contrato próprio.

| Item                    | Próximo entregável                                                                                     | Condição para implementar                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| Operação de alertas oficiais (R5) | Contrato ampliado de cobertura, expiração, monitoramento e disponibilidade do adaptador INMET. | Critérios operacionais e cobertura de produção definidos. |
| Validação e ampliação de previsão | Piloto offline para comparar `reference-v1` com dados históricos e avaliar cobertura ou horizonte maior. | Dataset reproduzível, baseline, revisão especializada e rollback definidos. |
| Contas e histórico (R6) | Contrato de identidade, autorização por recurso, retenção e exclusão.                                  | Público e necessidade de dados privados definidos.                     |
| Notificações (R6)       | Contrato de eventos/canais, adesão, cancelamento, idempotência e orçamento.                            | Identidade e fonte dos eventos disponíveis; destinatários autorizados. |
| Produção pública        | Plano de ambiente, cotas, secrets, domínio, coleta e rollback.                                         | Fornecedor/operador e valores reais definidos; homologação concluída.  |
| Validação do risco      | Protocolo de avaliação e revisão regional de limiares.                                                 | Especialista e conjunto de dados de avaliação definidos.               |

## Verificação estrutural deste planejamento

Executar os validadores da skill usando os caminhos completos dos arquivos
quando o pacote estiver fora de `.specs/`. O resultado deve ser registrado
no STATE do projeto. Não criar `validation.md` com PASS de implementação
antes de executar e verificar as tarefas.
