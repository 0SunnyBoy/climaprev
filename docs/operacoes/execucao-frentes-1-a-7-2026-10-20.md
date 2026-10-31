# Execução das sete frentes técnicas — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.
>
> Complemento do diagnóstico remoto: CI da base passou em 15/10; Security gates falhou na asserção de tema, cuja espera foi corrigida localmente. A revisão local ainda não foi enviada. develop sem proteção/checks obrigatórios; rulesets vazios. INMET segue sem confirmação real, inclusive nova tentativa com reset de conexão. Candidate-1 por último; prioridades atuais no RDP.

Estas são as sete frentes técnicas listadas na conversa, não as etapas do protocolo científico. Nenhuma autorização de ajuste/calibração/promoção foi inferida. A reference-v1 e a janela pública de sete datas permanecem; 14 dias continua apenas planejado. Repositório único e PDF acadêmico preservados.

## Estado vigente

| Frente | Entrega realizada | O que não está encerrado |
|---|---|---|
| 1. Alertas | Validade/expiração na entrega e cache; interseção temporal no fuso do local; Polygon com furos, MultiPolygon, validação de posições finitas/limites/anéis; cobertura inválida vira indisponível, não ausência | Conectividade real INMET não confirmada; geometrias antimeridiano/formatos não suportados são rejeitados conservadoramente |
| 2. Prazo global | Orçamento padrão de 7 s no serviço público, configurável até 8 s; cliente aguarda 10 s; cancelamento de tarefas e limpeza de locks testados; corrigida corrida de timers entre consultas | Timeout é cooperativo e aguarda cleanup. Transporte, parsing e rate limit anteriores ao serviço não fazem parte desse orçamento. Abort do navegador não garante interrupção imediata do trabalho remoto |
| 3. Interface | Contexto preservado ao voltar da emergência; foco de navegação; textos reativos ao idioma; ARIA/teclado da busca; tema/idioma persistidos; correção de overflow do cabeçalho | Testes automatizados não equivalem a avaliação manual completa com leitor de tela ou certificação WCAG |
| 4. CI | Workflow com builds separados, testes, lint, tipagem, auditoria Node, Composes e gate HTTPS; sintaxe/expressões aprovadas por actionlint 1.7.7 | Execução remota e checks obrigatórios do GitHub não confirmados; alterações locais não publicadas |
| 5. Observabilidade | Exporter Prometheus privado, registro temporário por worker em Redis, contadores e histogramas cumulativos; dois workers reais verificados; templates de painel/regras/retenção | Prometheus/Grafana/Alertmanager não provisionados; destinos de alertas, responsáveis, SLOs e retenção real dependem do ambiente futuro |
| 6. Carga | Cinco cenários de 60 s, dez usuários, recursos limitados, provedor sintético e dois workers; 3.000 requisições e zero falhas | Não mede capacidade máxima, 100 req/s, disponibilidade dos provedores reais ou capacidade da futura hospedagem |
| 7. Publicação | Pré-requisitos e sequência de release/rollback documentados | Hospedagem/provisionamento adiados por orientação explícita do usuário; sem publicação ou infraestrutura externa |

## Alertas oficiais

O contrato público conserva `available`, `unavailable` e `not_configured`. Se um registro compromete a confiança na cobertura, a resposta do fornecedor é tratada como indisponível, em vez de omitir o registro e declarar cobertura vazia. A política é conservadora e pode reduzir disponibilidade quando o feed contém registros malformados. Furos excluem pontos interiores; bordas de furos são incluídas conservadoramente. Não há equivalência com validação de impacto/desastre.

A validade é revista após a escrita opcional do cache para impedir entregar um aviso que expirou durante a consulta. O identificador do provedor na chave de cache foi atualizado para invalidar interpretações antigas. Há métricas dos estados de consulta de avisos, incluindo indisponibilidade.

`evidence/inmet-conectividade-2026-10-20.json` registra duas tentativas limitadas, com e sem herança de proxy de ambiente, ambas com `RemoteProtocolError`. Não foram retidos avisos reais. A compatibilidade sintética passou, mas não se declara integração ao vivo homologada enquanto essa dependência não puder ser verificada.

## Métricas compartilhadas

`CLIMAPREV_METRICS_AGGREGATION_ENABLED` é opt-in (false por padrão), habilitado explicitamente nos perfis de carga e homologação. Cada worker publica snapshot allowlisted de até 64 KiB a cada cinco segundos, com lease de 20 s. A leitura é limitada a 256 workers e deadline de dois segundos; conjunto incompleto/truncado/indisponível retorna 503. Não se usa `KEYS` para servir o exporter. Os contadores são mantidos por worker, evitando somar repetidamente snapshots cumulativos ou calcular média de percentis.

Endpoint: `/internal/metrics/prometheus`. Nginx público bloqueia `/internal/`; o scraper deve estar em rede privada. Os histogramas são cumulativos desde o início de cada processo; taxas agregadas devem usar `sum(rate(...))`, e p95 deve vir de `histogram_quantile` sobre os buckets somados. Workers encerrados podem permanecer no registro até o lease expirar. Dados históricos precisam ser retidos externamente, não no registro temporário Redis.

O provisionador de ACL inclui apenas os comandos adicionais `ZADD`, `ZRANGE` e `ZREMRANGEBYSCORE` dentro do namespace já restrito. Credenciais/ACLs antigas precisam de atualização controlada antes de habilitar a funcionalidade em um ambiente existente; não foram reescritas credenciais locais antigas silenciosamente.

Templates: `monitoramento/prometheus.yml`, `monitoramento/climaprev-alerts.yml`, `monitoramento/dashboard.json`. Retenção proposta: 30 dias em volume próprio. Limiares propostos: 5xx >1%, p95 HTTP global >2 s, fonte de avisos indisponível e scrape indisponível. São propostas operacionais; não SLOs aprovados por dados de produção. Templates não equivalem a serviços de monitoramento instalados ou alertas entregues.

## Campanha de carga local

| Cenário | Requisições | Falhas | req/s | p50 | p95 | p99 |
|---|---:|---:|---:|---:|---:|---:|
| Cache quente | 610 | 0 | 10,32 | 24 ms | 61 ms | 110 ms |
| Cache frio | 600 | 0 | 10,13 | 160 ms | 220 ms | 240 ms |
| Contenção de lock | 600 | 0 | 10,16 | 30 ms | 63 ms | 610 ms |
| Provedor lento | 590 | 0 | 10,07 | 540 ms | 580 ms | 610 ms |
| Redis com latência | 600 | 0 | 10,14 | 220 ms | 540 ms | 760 ms |

Taxa-alvo: dez requisições/s, tolerância ±10%, zero falhas e nenhum 429/5xx contado como sucesso. Os percentis são os agregados do Locust, incluindo priming quando aplicável; a duração nominal de cada cenário é 60 s. Não houve busca de janelas meteorológicas ou resultados favoráveis.

A bancada usa Docker Desktop compartilhado, API limitada a 2 CPU/512 MiB, provedor 1 CPU/256 MiB, Redis 0,5 CPU/128 MiB e gerador 1 CPU/512 MiB. São limites, não recursos exclusivos. Imagens com dependências travadas foram reutilizadas com código/testes atuais montados somente para leitura; um build redundante de ferramentas foi interrompido devido à transferência lenta de dependências. Não se apresenta esse ensaio como benchmark de uma imagem publicada. O snapshot de recursos é instantâneo, não medição de pico.

Evidência: `evidence/carga-local-2026-10-20/summary.json`, CSVs/logs e `resource-snapshot.jsonl`. O campo inicialmente chamado `started_utc` era timestamp de atualização do relatório; foi corrigido para `updated_utc`, com revisão registrada. O mock agora responde explicitamente com cobertura sintética vazia de avisos, sem simular ausência por erro HTTP. As datas de carga usam UTC atual para respeitar a janela pública.

## Verificação e limites

- Regressão completa: 644 testes backend aprovados em 55,80 s com warnings como erros; fontes/testes montados somente para leitura sobre runtime de dependências travadas.
- Frontend: 27 testes aprovados; build/typecheck/ESLint aprovados, incluindo tradução reativa de erros por campo após resposta 422 e correção responsiva do cabeçalho.
- Ruff completo e mypy Linux em 68 módulos aprovados. Workflow aprovado pelo actionlint local, sem alegar execução GitHub.
- Navegador: datas/422, busca por teclado e ARIA, consulta real à API, contexto/foco após emergência, tema/idioma persistentes, seis pares semânticos de cores com contraste ≥4,5 em claro/escuro, ausência de overflow a 320/375/768/1280 px, erro 503, 429/cooldown, bloqueio CORS e interface disponível com API parada.
- Imagem runtime construída e verificada: UID 10001, pacote de produção presente, sem testes/documentação/arquivos de ambiente/ferramentas de desenvolvimento.
- TLS local: CA/hostname verificados separadamente; navegador com pin SPKI limitado ao processo, sem alterar confiança global.

O primeiro gate responsivo encontrou overflow em 320 px. Corrigiu-se a quebra de linha do cabeçalho; o teste não foi enfraquecido. A configuração científica, os alvos observacionais e o horizonte de 14 dias não foram alterados.

## Preparação documental da publicação futura

Quando houver ambiente e autorização para publicar: revisar diff e identificar commit; executar CI remota e checks obrigatórios; construir imagens imutáveis e registrar digests; definir operador, DNS/TLS público, segredos/ACL, quotas e orçamento de provedores; configurar monitoramento e destinos de alertas; aprovar smoke/readiness; executar rollout e demonstração de rollback para os digests anteriores. Redis de cache é descartável, mas credenciais, histórico de métricas e evidências têm retenções próprias. Incidente de avisos indisponíveis não autoriza apresentar risco baixo por ausência de fonte.

Hoje não há destino de hospedagem preparado. Essa frente permanece adiada conforme pedido do usuário, sem alegar produção pronta ou rollback de produção demonstrado. A pendência científica da candidata continua independente das entregas técnicas acima.
