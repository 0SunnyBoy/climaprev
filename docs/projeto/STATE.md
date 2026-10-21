# STATE — ClimaPrev

## Qualificação do lote refatorado — 21/10/2026

Lote de responsividade, refatoração transversal e redução de linhas preparado para publicação na develop por solicitação do usuário. Validação local mais recente: 659 testes backend, 32 frontend, build/lint/tipagem e contrato preservados. O estado Git/SHA e a aprovação remota devem ser conferidos no commit e nos Actions correspondentes; resultados locais não substituem os checks desse SHA. Os registros de 20/10 abaixo descrevem o checkpoint anterior ao envio e não devem ser interpretados como confirmação de alterações ainda não commitadas após a publicação.

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
