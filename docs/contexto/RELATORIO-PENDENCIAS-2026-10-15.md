# Pendências após cruzamento com a pasta de contexto

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 15/10/2026, America/Sao_Paulo. Branch de trabalho definida pelo usuário: `develop`.

## Parecer

As 12 frentes F01–F12 do contexto continuam pertinentes à implementação local. Nenhuma pode ser encerrada integralmente apenas pela comparação de arquivos. Há componentes já implementados em várias delas, e há pendências de evidência científica/operacional que não são ausência de código.

Os manifestos conferidos coincidem com a pasta atual: 251 registros incluindo imagens, sem divergências. A origem Git ainda precisa ser vinculada de forma verificável ao histórico original caso se deseje continuidade desse histórico. O Git criado nesta sessão está em develop, sem commits e sem remoto.

Prioridades abaixo são recomendações desta análise: P1 = tratar antes do aceite a que se aplica; P2 = consolidar qualidade/manutenção. Não são evidência de incidente em produção.

## Matriz de situação

| ID | Frente | Situação | Prioridade/condição |
| --- | --- | --- | --- |
| F01 | Horizonte e datas | Lacuna confirmada no schema e formulário | P1 funcional |
| F02 | Qualidade e métricas históricas | Ferramenta existe; avaliação incompleta | P1 antes de validar/ampliar políticas |
| F03 | Ciência e calibração | Camada existe; aprovação não demonstrada | P1 antes de alegar melhoria de precisão |
| F04 | Alertas INMET | Integração existe; validade/qualidade incompletas | P1 funcional/operacional |
| F05 | Deadline da consulta | Tetos desalinhados; etapas sequenciais | P1 funcional/operacional |
| F06 | Observabilidade agregada | Métricas existem; armazenamento por processo | P1 para publicação |
| F07 | CI e reprodução | Lint/Vitest ausentes dos workflows | P1 para promoção |
| F08 | Implantação pública | Estrutura existe; aceite público não demonstrado | P1 para publicação |
| F09 | Gate e homologação | Falha histórica registrada; reprodução pendente | P1 para promoção/publicação |
| F10 | Capacidade atual | Harness e baseline histórico existem | P2; elevar conforme demanda |
| F11 | Acessibilidade e busca | Smokes existem; erros da busca ocultados | P2 de qualidade |
| F12 | Documentação | Contradições atuais confirmadas | P2 transversal |

## F01 — Limitar datas ao suporte real

**Confirmado:** `src/climaprev/api/schemas/risk.py` valida ordem e sete dias inclusivos, mas não compara o intervalo com o dia atual nem com o horizonte do provedor. Os campos de data em `frontend/src/components/QueryForm.vue` não possuem min/max temporal.

**Impacto:** intervalos sem suporte podem alcançar o provedor externo, consumir orçamento e gerar falhas ou respostas pouco claras.

**Restante:** definir o contrato temporal com o fuso da localidade; aplicar limites na API e interface; garantir rejeição antes da chamada de previsão. Determinar o suporte do provedor no momento da implementação, sem presumir que a duração máxima de sete dias equivale ao horizonte disponível.

**Aceite:** passado, hoje, último dia permitido, primeiro inválido, período inclusivo e viradas de dia/fuso testados; API e UI com o mesmo contrato.

## F02 — Completar a validação histórica

**Já existe:** coleta em `src/climaprev/tools/validate_historical.py` e avaliador em `src/climaprev/domain/risk_validation.py`.

**Confirmado:** nulos são filtrados; precipitação soma valores disponíveis sem cobertura horária mínima; só a interseção de dias é avaliada; `missing_fields=()` não comunica perdas; o relatório contém casos, acertos, falsos positivos/negativos e acurácia, sem matriz multiclasses completa ou precisão/recall/F1 estratificados.

**Impacto:** dias incompletos podem aparentar qualidade maior do que têm; comparar classificações heurísticas sobre reanálise não comprova previsão de impactos observados. Os contadores atuais representam direção do erro na ordem low/moderate/high, não substituem métricas completas por classe/evento.

**Restante:** registrar cobertura esperada/obtida, exclusões e motivos, parâmetros, origem/modelo/dataset, coleta e entradas reproduzíveis; ampliar localidades, épocas e antecedências; separar ajuste e avaliação. Calcular matriz e métricas por classe/evento/região/antecedência, documentando denominadores e amostra.

**Aceite:** relatório reproduzível com dados insuficientes sinalizados, amostra representativa e limitações explícitas. A amostra histórica curta de Belém citada na documentação não aprova os limiares.

## F03 — Aprovar políticas e perfis de calibração

**Já existe:** `ForecastCalibration` em `domain/bias_correction.py`, aplicação no serviço e identidade do perfil na chave de cache. O padrão é disabled.

**Restante:** usar F02 para avaliar a baseline `reference-v1` e candidatas; revisar limiares e coeficientes com especialista; definir separação de dados, critérios de promoção, versão e rollback.

**Aceite:** comparação baseline/candidata em dados de teste separados e decisão revisada registrada. Manter disabled enquanto a evidência não sustentar promoção. Não recriar a camada nem apresentar sua existência como ganho científico comprovado.

## F04 — Validade, atualização e cobertura dos alertas

**Confirmado:** `_get_official_alerts` em `application/services/forecast_query.py` retorna conteúdo de cache sem consultar sua expiração/stale próprios ou revalidar a validade de cada aviso na entrega. O adaptador `infrastructure/providers/inmet_alerts.py` aceita Polygon, utiliza o primeiro anel e descarta registros inválidos/não suportados sem contrato de cobertura parcial.

**Correção de interpretação:** a implementação já retorna `unavailable` em falha e distingue `available`/`not_configured`. A pendência não é criar essa distinção do zero; é preservá-la e complementá-la para respostas parcialmente inválidas, atualização e avisos vencidos.

**Restante:** definir política para avisos ativos/futuros/vencidos e sua relação com o período solicitado; expor coleta e qualidade própria; tratar anéis internos e geometrias suportadas ou sinalizar limitações; medir descartes, falhas e latência. Avaliar cache compartilhado do feed se a medição justificar.

**Aceite:** testes de expiração durante o cache, stale, fonte indisponível, nenhum aviso, geometria com buraco/não suportada e resposta parcialmente inválida. Falha/cobertura incompleta não pode ser apresentada como garantia de ausência de alertas.

## F05 — Coordenar o prazo total da consulta

**Confirmado:** `useRiskQuery.ts` aborta em 10.000 ms; `config.py` permite 20 s para operação HTTP externa; a espera do lock tem deadline de 30 s. Localização, previsão e alertas são aguardados em sequência no serviço. Esses números são configurações, não latências observadas.

**Já existe:** controle de cancelamento, heartbeat e liberação de lock. O trabalho é integrar esses mecanismos a um contrato total, sem pressupor ausência de limpeza atual.

**Restante:** medir etapas; definir orçamento global e prazo restante compartilhado por espera, chamadas e retries; avaliar concorrência entre previsão e alertas depois da localização; limitar a etapa opcional INMET; preservar fallback válido e limpeza no cancelamento.

**Aceite:** lentidão de cada fonte, contenção, timeout, cancelamento e perda do lock cobertos; término dentro do contrato e nenhuma tarefa órfã. Comparar latência/erros antes e depois sem escolher novos tetos arbitrários.

## F06 — Operar observabilidade entre instâncias

**Confirmado:** `api/observability.py` mantém Counter/deque em memória; `api/routes/metrics.py` expõe snapshot. Há percentis e métricas de cache/provedor/lock; reinícios perdem histórico, e workers têm estados separados.

**Restante:** coletor/exporter e agregação de workers/réplicas, retenção externa, painéis e alertas de disponibilidade, latência, erros, stale, locks, Redis e INMET; definir objetivos e responsáveis, preservando sanitização e limites de cardinalidade.

**Aceite:** dados de todas as instâncias, continuidade após reinício e detecção de falhas simuladas. Logs existentes não substituem automaticamente séries métricas agregadas.

## F07 — Completar checks e ambiente reproduzível

**Confirmado:** `.github/workflows/ci.yml` executa pytest/Ruff/mypy e smokes; o build frontend inclui vue-tsc/Vite. Nem ele nem `security.yml` executam os scripts ESLint e Vitest. `frontend/Dockerfile` chama apenas build após instalação. Há scan Trivy de imagem previsto, mas nenhuma auditoria Node explícita nos workflows.

**Confirmado também:** produção/build Python têm locks com hashes; as ferramentas adicionais `[dev]` de `pyproject.toml` não possuem lock completo equivalente. As constraints de produção do Dockerfile reduzem variação, mas não fixam todo o ambiente de teste.

**Restante:** incluir lint/testes frontend como checks de promoção; definir auditoria de dependências Node; fixar dependências transitivas de teste; alinhar README e comandos; verificar no GitHub se proteções/rulesets realmente tornam checks obrigatórios. Isso não é inferível apenas do YAML.

**Aceite:** lint, Vitest, build/typecheck, backend e segurança aprovados para a versão promovida, com instalação reproduzível e política de bloqueio verificável.

## F08 — Preparar publicação real

**Já existe:** Docker/Compose, homologação sintética, TLS/ACL de teste, runbooks e workflows. Não há deploy automatizado nesses workflows. Ausência de evidência nesta análise não prova inexistência de ambiente público fora da pasta.

**Restante:** escolher ambiente e operador; DNS/TLS públicos, rede, secrets, cotas, artefatos, promoção, readiness, observabilidade e rollback; ensaiar recuperação, renovação e rotação no ambiente escolhido. Declarar se a promoção será automatizada ou um procedimento manual controlado.

**Aceite:** versão identificável e acessível, superfícies internas protegidas, gates aprovados, monitoramento e rollback demonstrados, com evidência de imagem/dependências na publicação.

## F09 — Reproduzir falha e completar homologação

**Evidência histórica do ZIP:** CI de 7190797 aprovada; Security gates falhou no navegador e pulou homologação/TLS, rotação, scan runtime e regressão posterior. Não houve nova consulta remota nem reprodução nesta sessão.

**Indício confirmado no código:** `useTheme.ts` aplica mudança animada em requestAnimationFrame; `_check_theme_toggle` em `tests/docker/check_frontend_browser.py` verifica `dataset.theme` imediatamente com assert/evaluate após clique. Há uma hipótese plausível de corrida, mas não uma causa comprovada da execução histórica.

**Restante:** obter/revisar traceback e reproduzir com o runner da revisão; corrigir sincronização/comportamento conforme o diagnóstico, preservando asserções funcionais; executar todos os gates subsequentes; concluir revisão independente e homologação do ambiente real.

**Aceite:** navegador e gates posteriores aprovados na revisão escolhida; nenhum gate exigido ignorado; resultados e limitações operacionais registrados. Não marcar segurança integralmente aprovada a partir do sucesso isolado da CI.

## F10 — Atualizar capacidade da versão

**Já existe:** `tests/load/locustfile.py`, cenários e provedor mock. O handoff registra baseline histórico de 60.000 requisições/600 s; não é medição nova desta pasta.

**Restante:** executar em ambiente dedicado com versão/hardware/configuração registrados; medir throughput, p50/p95/p99, erros, quotas e recursos por cenário; definir metas e gargalos. Separar recusa por quota de esgotamento computacional e resultados com mock de disponibilidade das fontes públicas.

**Aceite:** relatório ligado à versão promovida e metas de capacidade verificáveis. Não repetir carga pesada contra provedores públicos para medir capacidade interna.

## F11 — Avaliação assistiva e recuperação da busca

**Já existe:** aceitação de DOM/teclado/foco, responsividade, tema e idioma.

**Confirmado:** `frontend/src/services/api.ts` transforma resposta HTTP não OK da busca em `[]`; `useLocationSearch.ts` não expõe estado próprio de erro. Isso torna indisponibilidade difícil de distinguir de nenhuma sugestão. Não há evidência de avaliação formal com leitor de tela nos registros examinados.

**Restante:** comunicar erro e recuperação/repetição da busca; avaliar leitor de tela, contraste e rede lenta; registrar roteiro, resultados e tratamento de achados. Preservar cancelamento e proteção contra resultados antigos.

**Aceite:** navegação assistiva e falhas HTTP/rede avaliadas com evidência; usuário distingue erro de busca sem resultados. Pontuação automática não substitui esses fluxos manuais.

## F12 — Alinhar documentação ao estado real

**Confirmado:** README afirma que localStorage guarda somente tema, embora `useLocale.ts` persista idioma. Documentos de projeto ainda mencionam V3, alterações sem commit/push, cópias sem Git e próximos passos duplicados. Handoff registra revisão aprovada enquanto STATE/catálogo registram revisão final pendente, sem uma identificação uniforme da versão a que cada afirmação se aplica.

**Restante:** atualizar README, PROJECT, STATE, ROADMAP, handoff e catálogo; identificar cronologia e versão dos aceites; separar histórico de instruções atuais; distinguir CLI com coleta pela rede do avaliador offline; registrar ambiente Windows/Git atual e decisões arquiteturais relevantes.

**Aceite:** documentos concordam com código, branch/revisão, preferências persistidas, gates e backlog. Não exigir publicação inicial ou criação de componentes já existentes. Corrigir links históricos conforme sua função, sem tratar automaticamente as 151 referências catalogadas no ZIP como defeitos funcionais.

## Pendências adicionais desta cópia e do pacote

1. **Proveniência Git:** decidir vinculação ao histórico original antes de integração/push. A criação de um primeiro commit independente não recuperaria 7190797. Git/identidade/develop solicitados já estão configurados; não há remoto ou commit.
2. **Ambiente local:** disponibilizar execução compatível com Python 3.12 e ferramentas do projeto ou Docker para reproduzir os gates. A análise atual não fornece nova aprovação de testes.
3. **Cobertura do contexto:** acrescentar hashes de `docker/build-requirements.in` e `tests/docker/Playwright.Dockerfile` aos próximos índices. São arquivos existentes não comparáveis pelo pacote atual.

Esses itens não substituem F01–F12 e não são defeitos novos de lógica da aplicação.

## Ordem recomendada de execução

1. Consolidar proveniência/ambiente e reproduzir F09; completar F07.
2. Corrigir contratos funcionais F01, F04 e F05, com testes dirigidos.
3. Executar F02 e usar seus resultados para F03; não ativar calibração antecipadamente.
4. Operar F06 e medir F10 na revisão escolhida.
5. Completar F11 e manter F12 atualizado a cada entrega.
6. Concluir F08 com aceite real, revisão independente e gates finais de F09.

F02 é dependência de F03; F06/F10 sustentam F08. A liberação de uma versão posterior exige evidências correspondentes àquela versão, não apenas aos testes históricos de 7190797.

## Escopo futuro condicionado

Contas, favoritos, histórico pessoal, notificações, horizonte maior, regras regionais e catálogo internacional de emergência dependem de decisão de produto e contratos próprios. A página de emergência existente não comprova o catálogo internacional proposto. Mapas, mobile e ML não foram convertidos em pendências obrigatórias da consulta anônima.

## Limites e entregáveis

Esta revisão leu contexto, manifestos, workflows e implementação relevante às pendências e comparou integralmente os registros dos manifestos. Não houve testes da aplicação, acesso meteorológico, medição de carga, auditoria atual de vulnerabilidades, deploy ou alteração de código.

Entregáveis: este relatório, `docs/contexto/RELATORIO-COMPATIBILIDADE-CONTEXTO-2026-10-15.md` e `comparacao-contexto-2026-10-15.csv`. O relatório de compatibilidade detalha método, contagens, integridade, limitações e estado Git.
