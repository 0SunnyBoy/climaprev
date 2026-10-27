# STATE — ClimaPrev

## Consolidação em 27/10/2026

Regressão integral local aprovada: **748 testes backend** (warnings como erros), mypy em **82 módulos**, Ruff e hardening local. O lote inclui coleta/comparação experimental, regressões dos avisos e melhoria da mensagem acessível de limite de requisições. Lockfile do frontend atualizado para corrigir os dois achados moderados do Vitest; auditoria após correção sem vulnerabilidades. Publicação e qualificação remota serão registradas no relatório desta consolidação.

Permanecem pendentes: teste auditivo real PT/EN; aceite dos parâmetros/calendário científicos e controle D+7; pareamento das demais variáveis; cobertura do calendário e incerteza estatística; coleta recorrente após aceite; refinamento e integração condicionados à evidência. Reference-v1 permanece ativa, sem campanha confirmatória iniciada ou ganho comprovado da candidate-1. Horizonte de 14 dias e hospedagem adiados.

## Comparador exploratório e elegibilidade — 26/10/2026

Entrada da baseline diária, pareamento v2 com tempos explícitos e comparação consolidada de chuva implementados. Interseção justa de casos, cobertura/exclusões, métricas numéricas e detecção diagnóstica, estratos por estação/dia após coleta e D+7 sem controle explicitamente indefinido. [Relatório](../operacoes/comparacao-experimental-2026-10-26.md). 75 testes direcionados, mypy dos três módulos e Ruff aprovados; sem nova suite completa, resultados sobre dados reais ou push. Padrão exige rodada informada; modo de coleta/retrospectivo requer opção explícita. Nenhuma aprovação científica ou promoção automática. Controle científico de D+7 e parâmetros finais continuam pendentes.

## Verificação dos avisos — 26/10/2026

Confirmada a entrega de chuva, vento, calor/frio e condições simultâneas em cenários controlados, do caso de uso à rota e nos componentes Vue. Corrigida exibição de `celsius`/`fahrenheit` para °C/°F no resumo, sem alterar cálculo. **32 testes backend selecionados e 48 frontend, lint/tipagem/build aprovados.** [Relatório e alcance](../operacoes/verificacao-avisos-2026-10-26.md). Sem consulta INMET ao vivo ou diagnóstico da consulta original. Sem novo push; a regressão completa anterior de 714 backend continua identificada como checkpoint separado.

## Incremento vigente — 26/10/2026

Baseline pelo adaptador e política atuais arquivável, seleção automática preservada como origem desconhecida, Single Runs com inicialização explícita, manifestos com versões de pipeline, ledger SQLite com cotas/deduplicação entre executores locais e runner por slot desativado por padrão. Pareamento exploratório de chuva por estação/intervalo implementado e exercitado em dados já conhecidos de 2024. [Relatório de implementação](../../RELATORIO-IMPLEMENTACAO-2026-10-26.md).

Qualificação local final: **714 testes backend, 33 frontend, mypy Linux em 81 módulos, Ruff e hardening local aprovados**. Baseline/rodadas GFS e IFS verificadas pontualmente ao vivo. Replay exploratório A201: 28 datas, nove pares completos, 19 incompletos; coleta retrospectiva, sem métrica de ganho ou aceite confirmatório. Sem novos outcomes reservados ou fitting.

Base publicada permanece `5a6fc9c`; novos incrementos sem commit/push ou CI remoto. Reference-v1 e janela pública preservadas. A baseline cobre adaptador/política, sem cache/alertas, e não fornece D+7 fora da janela pública. Rodada solicitada não é primeira publicação comprovada. Pareamento de outras variáveis, parâmetros finais e acionador da campanha continuam pendentes; nenhum agendamento recorrente foi criado. Registros anteriores de ausência desses componentes são históricos.

## Coletores e normalização experimental — 23/10/2026

Implementados coletores pontuais GFS/IFS025/ICON e MET Norway com HTTP limitado e sem retries, junto de medições UTC/unidades/intervalos e soma de chuva por cobertura exata, sem sobreposição/prorrateio. Independentes da API pública. [Execução e limites](../operacoes/coleta-experimental-2026-10-23.md).

Preflight Docker nos três pontos municipais: 11 de 12 combinações aceitas; IFS/Porto Alegre rejeitado por chuva negativa. GFS/IFS válidos cobrem os dias após coleta D+1/D+3/D+7; ICON D+7 e MET D+3/D+7 incompletos nesta amostra, explicitamente sem totais elegíveis. Rodada de inicialização desconhecida; não declarar essas etiquetas como antecedências científicas comprovadas. TLS ativo. 57 testes selecionados, mypy dos três módulos e Ruff no host aprovados. Sem suíte completa ou CI remoto do novo lote.

Permanecem pendentes baseline automática, identificação comprovada de rodada, pareamento observacional, orçamento compartilhado/agendamento e parâmetros finais da campanha. Sem coleta recorrente, fitting ou promoção; alterações locais sem commit/push. Os registros abaixo de "sem HTTP/normalização" descrevem o incremento anterior, agora superado por este protótipo.

## Preparação da coleta experimental — 23/10/2026

[Catálogo de fontes e sequência de coleta](../planejamento/reference-candidate-1/fontes-e-coleta-2026-10-23.md): GFS/IFS/ICON explícitos priorizados e MET Norway exploratório, com restrições de origem, horizonte e acesso verificadas documentalmente. Preflight ao vivo e integração dos novos adaptadores ainda pendentes.

Implementado `tools/experimental_archive.py`: envelope de JSON bruto com origem/local, horário UTC de coleta/rodada/validade, hashes, escrita sem sobrescrita e flags para rodada desconhecida/coleta tardia. Separado da aplicação pública, sem HTTP, normalização meteorológica ou agendamento. Docker: 34 testes selecionados e mypy do módulo aprovados; Ruff dos arquivos novos aprovado. Não representa execução integral de regressões ou ganho de previsão. Alterações locais sem commit/push.

[Parâmetros de campanha propostos](../planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md) preparados para revisão: três estações, ensaio técnico de 14 dias e teste de um ciclo anual, com margens físicas/estatísticas explicitamente não aprovadas. O ensaio técnico não amplia o horizonte público. Coleta confirmatória e promoção aguardam fechamento do desenho.

## Direção científica aprovada — 23/10/2026

Usuário aprovou a direção após esclarecer o escopo multivariável: chuva diária D+1 como objetivo inicial, D+3/D+7 e temperatura/vento/umidade/risco como avaliações complementares, meta inicial de 5% de redução de MAE com evidência favorável, teste independente e proteção de extremos. [Registro de aceite e limites](../planejamento/reference-candidate-1/aprovacao-direcao-2026-10-23.md). Campanha, equivalência instrumental, margens, suporte e desenho estatístico ainda precisam ser fechados antes do teste confirmatório. Não equivale a aprovação final do experimento ou da candidata; reference-v1 preservada. Registro local sem commit/push nesta atualização.

## Continuação vigente — 21/10/2026

Base publicada: `5a6fc9c`, CI [39645243749](https://github.com/0SunnyBoy/climaprev/actions/runs/39645243749) e Security gates [39645243757](https://github.com/0SunnyBoy/climaprev/actions/runs/39645243757) aprovados. Os registros de qualificação abaixo preservam o histórico das tentativas anteriores.

Incremento local posterior: aviso 429 estabilizado para impedir alteração da região de alerta a cada segundo; contador visual separado e mensagem de liberação preservados. Regressão no App, 33 testes frontend, lint, tipagem e build aprovados. Ensaio auditivo ainda pendente; sem commit/push deste incremento e sem nova qualificação remota. [Execução e roteiro](../operacoes/acessibilidade-continuacao-2026-10-21.md).

Usuário escolheu revisar a proposta científica detalhada antes de aprovar. [Proposta para revisão](../planejamento/reference-candidate-1/proposta-cientifica-para-revisao-2026-10-21.md): objetivo, comparadores, semântica das variáveis, dados prospectivos, métricas e condições de promoção. Status proposto/não aprovado, sem objetivo primário escolhido, fitting ou nova leitura de outcomes reservados. Reference-v1 preservada.

## Qualificação do lote refatorado — 21/10/2026

Refatoração publicada na develop em `e448afc`. A primeira execução remota aprovou a integração independente por HTTPS, mas bloqueou a auditoria de dependências (Vite) e a varredura histórica (hash público do contrato OpenAPI). Correção: Vite 6.4.5 e exceção Gitleaks restrita ao valor exato do SHA256 público, sem desativar regras. Verificações locais da correção: 32 testes frontend, lint, build/tipagem, auditoria sem vulnerabilidades, política sintética de segredos e histórico de 53 commits sem achados. A aprovação remota da correção deve ser consultada nos Actions do novo commit.

Lote de responsividade, refatoração transversal e redução de linhas preparado para publicação na develop por solicitação do usuário. Validação local mais recente: 659 testes backend, 32 frontend, build/lint/tipagem e contrato preservados. O estado Git/SHA e a aprovação remota devem ser conferidos no commit e nos Actions correspondentes; resultados locais não substituem os checks desse SHA. Os registros de 20/10 abaixo descrevem o checkpoint anterior ao envio e não devem ser interpretados como confirmação de alterações ainda não commitadas após a publicação.

Na execução de `432294a`, o CI completo passou; o Security gates avançou até a imagem de runtime e identificou GHSA-6q48-6c7w-9gw2 em certifi. Atualizados os locks de produção, desenvolvimento e carga para certifi 2026.10.19, com hashes dos dois artefatos oficiais do PyPI. Referência: https://github.com/advisories/GHSA-6q48-6c7w-9gw2. A confirmação final de segurança depende da nova execução sobre o commit dessa correção.

## Estado vigente — 20/10/2026

- **Versão/Git:** backend e frontend 0.1.0 em desenvolvimento; develop, HEAD e referência local origin/develop em `451d845`. Esse lote INMET/busca foi enviado anteriormente. Responsividade e refatoração posteriores locais, sem commit/push, merge em main, release ou deploy. CI desse diff não executado remotamente; aprovação antiga não cobre o novo código.
- **Aplicação:** API FastAPI, frontend Vue/TypeScript/Vite e Redis. Builds e Composes distintos, CORS/CSP e gate HTTPS local existentes; monorepo preservado. Sem hospedagem definida.
- **Datas/prazos:** hoje UTC até +6, até sete dias por consulta. Orçamento cooperativo do serviço 7 s, máximo configurável 8 s; cliente 10 s, busca de cidades 5 s após debounce. Transporte/validação anteriores ao serviço e cleanup limitam a interpretação do orçamento. Cancelamento encerra a espera mesmo se o transporte ignorar abort, com isolamento de resposta tardia.
- **Alertas:** filtro temporal/geográfico conservador, cache/expiração na entrega, Polygon/MultiPolygon com furos. INMET ao vivo verificado em amostra controlada, inclusive Docker; não é garantia de cobertura/uptime. Política reference-v1 preservada.
- **Responsividade:** etapa 1 concluída localmente; telas 320/375/768/1280 px, PT/EN, consulta real de sete dias e foco do resultado verificados. Medição isolada de três cidades: frias 1,20–2,16 s e repetidas 3,57–4,21 ms; falha e travamento injetados tratados. Não é capacidade de produção. [Evidências e limites](../operacoes/responsividade-2026-10-20.md).
- **Refatoração:** utilitário de prazo compartilhado; DTOs/conversões em query_result, codecs em cache_codec e schemas/mapper HTTP em risk_response. Resolução de local, cache/lock/heartbeat e consulta de avisos em serviços próprios; tratamento de erros/saúde fora do main. Validadores frontend separados, configuração ESLint consolidada, flags de código sem uso e gate de hardening efetivo ativos. Doubles de testes em suporte próprio, exceções canônicas na aplicação e shim redundante removido. Serviço e rota menores; removidos imports e alias Any dispensáveis. OpenAPI canônico idêntico ao HEAD anterior; sem alteração de política, cache ou algoritmos científicos. [Execução](../operacoes/refatoracao-2026-10-20.md).
- **Validação:** 32 testes frontend, build/tipagem/ESLint/Ruff e mypy Linux (75 módulos) aprovados. Suíte completa mais recente de **659 testes backend aprovada em 55,18 s**, com warnings tratados como erros, incluindo as oito regressões do gate de hardening. Tentativa Windows interrompida não é aprovação.
- **Acessibilidade:** teclado/ARIA/contraste/layout e inspeção interativa realizados; ensaio auditivo com leitor de tela ainda pendente por indisponibilidade informada pelo usuário. Não declarar certificação WCAG.
- **Ciência:** CSVs oficiais, baseline, comparação espacial e catálogo preparados; resultados mistos, sem superioridade substancial comprovada. Reservas com independência não demonstrada. Usuário responsável pelo aceite; critérios/fontes/protocolo aguardam decisão. Nenhuma calibração, combinação de modelos ou promoção implementada.
- **Múltiplas fontes:** planejadas comparação e normalização por modelo/rodada/antecedência e avaliação com INMET; pesquisar Open-Meteo explícita e MET Norway. APIs distintas podem repetir o modelo de origem. Código aberto e possível serviço comercial exigem licença, atribuições e acesso compatíveis; endpoint gratuito não é autorização comercial automática.
- **Operação:** exporter privado por worker/Redis e templates existentes; Prometheus/Grafana/Alertmanager não instalados. Carga sintética anterior: 3.000 requisições, zero falhas e maior p95 580 ms, sem certificação de capacidade. develop sem proteção/checks obrigatórios registrados; nenhuma regra administrativa alterada.

## Revisão de linhas e abstrações

Redução desta revisão: 109 linhas físicas (18.408 → 18.299), sem apagar testes. Saldo contra o commit: +195, dos quais +168 testes/gates e +27 código executável; a contagem anterior misturava essas categorias. Mapeamento HTTP, wrappers e tipo duplicado simplificados; contrato preservado em 24 cenários JSON e OpenAPI. [Análise e método](../operacoes/reducao-linhas-2026-10-20.md).

## Próximos trabalhos

Seguir [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md): concluir acessibilidade quando possível, fechar protocolo científico, selecionar fontes, coletar/normalizar, comparar, refinar e integrar candidata qualificada. Serviços de cache/locks/avisos já separados nesta refatoração; identidade de modelo e cache antecede integração operacional de múltiplas fontes. Não bloquear o desenho científico com reorganização cosmética.

Adiadas: hospedagem/monitoramento no ambiente definitivo, horizonte de 14 dias (somente planejado) e separação de repositórios. PDF acadêmico fora do escopo. Documentos correntes consolidados sem apagar protocolos, resultados ou evidências históricas.

## Histórico e evidências

[Arquivo histórico](STATE-HISTORICO-ATE-2026-10-20.md) · [frentes 1–4](../operacoes/frentes-1-a-4-2026-10-20.md) · [frentes 1–7](../operacoes/execucao-frentes-1-a-7-2026-10-20.md) · [estado dos protocolos](../planejamento/reference-candidate-1/estado-dos-protocolos-2026-10-20.md). Esses relatórios registram checkpoints; não redefinem o estado vigente acima.
