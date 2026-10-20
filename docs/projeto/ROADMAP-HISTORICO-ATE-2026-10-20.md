# Arquivo histórico — ROADMAP

Este arquivo preserva registros de lotes anteriores, inclusive resultados e pendências superadas. **Não é o estado atual da aplicação.** Consulte [ROADMAP](ROADMAP.md) e [RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md). Os caminhos relativos históricos foram mantidos.

## Histórico anterior — não usar como status vigente

## Prioridades atuais — 19/10/2026

1. Concluir adequação científica das observações, suficiência, reserva e critérios
   do protocolo; congelar alvos observacionais sem ajustar a reference-v1.
   A reconciliação numérica da chuva de Belém foi concluída; falta aprovação da
   adequação da fonte e dos critérios, com suporte alto ausente em calor/frio.
2. Completar os contratos de datas, alertas e prazo global da consulta.
3. Obter o runner fixado e executar gates de navegador; espera pelo estado do
   tema já foi corrigida no teste, mas sua execução permanece pendente.
4. Concluir acessibilidade, capacidade em ambiente dedicado, observabilidade
   agregada e preparação da publicação. Os smokes locais não aprovam produção.
5. Avaliar candidata somente depois de revisão e nova autorização para ajuste.

As entregas de 19/10 estão no [estado atual](STATE.md) e no
[RDP](../../RELATORIO-PENDENCIAS-2026-10-19.md). O plano datado abaixo é histórico.

**Data:** 23 de setembro de 2026.
**Estado:** implementação local até P2.6 concluída; branch conectada ao Git;
commit, push e revisão independente final pendentes.

O progresso detalhado está em [STATE](STATE.md), e o catálogo técnico está em
[Implementations and refactoring](ImplementationsAndRefactoring.md).

## Etapas do produto

| Etapa | Objetivo | Estado atual |
| --- | --- | --- |
| R0 — Documentação | Consolidar arquitetura, contratos e limites. | Concluída; documentação sincronizada nesta revisão. |
| R1 — Consistência dos dados | Resolver fuso, cobertura horária, valores inválidos e completude. | Concluída no ciclo T1–T5. |
| R2 — Falhas e configuração | Tratar stale, falhas do provedor, lock e configuração. | Concluída no ciclo T6–T10 e incrementos P1.6/P1.11. |
| R3 — Segurança e operação | Definir proxy, logs, cotas, imagem, redes e métricas. | Concluída no ciclo T11–T20 e incrementos P1.1–P1.9. |
| R4 — Frontend | Entregar consulta, resultado, recuperação e acessibilidade. | Concluída no ciclo T21–T25 e incrementos P0/P2.3/P2.5/P2.6. |
| R5 — Alertas oficiais | Integrar fonte autorizada sem misturar alertas ao risco heurístico. | Integração básica do INMET concluída em P2.1; contrato operacional ampliado ainda pendente. |
| R6 — Personalização | Avaliar contas, favoritos, histórico e notificações. | Pendente; exige contratos próprios de identidade e dados. |

As 25 tarefas do ciclo base estão concluídas. Os incrementos P0–P2.6
estenderam o ciclo com separação do frontend, integração do INMET, busca de
localidades, controle de consultas e acessibilidade. A revisão independente
final ainda precisa ser executada.

## Decisões e limites

| ID | Decisão | Estado |
| --- | --- | --- |
| DEC-01 | A consulta permanece anônima neste ciclo. | Mantida; operações pessoais ficam fora. |
| DEC-02 | O período máximo permanece em sete dias inclusivos. | Mantida e validada. |
| DEC-03 | A completude usa `complete`, `partial` e `unavailable`. | Implementada e exposta na API e no frontend. |
| DEC-04 | O ambiente local usa Nginx para frontend e API FastAPI separada. | Implementada. |
| DEC-05 | O risco permanece heurístico e orientativo. | Mantida; calibração científica pendente. |
| DEC-06 | O INMET é a fonte oficial integrada nesta etapa. | Implementada em P2.1; cobertura e operação precisam de consolidação futura. |
| DEC-07 | Alertas oficiais permanecem separados de `forecast_risk`. | Implementada. |
| DEC-08 | Dados pessoais, contas e notificações ficam fora deste ciclo. | Mantida; revisar antes de criar identidade ou histórico. |

## Entregas concluídas

- Frontend estático em `frontend/`, servido pelo Nginx local.
- Backend FastAPI sem responsabilidade de servir HTML ou assets.
- Consulta de risco disponível por GET e POST.
- Proxy confiável, rate limit e headers de segurança configurados.
- Containers e rede local endurecidos.
- Cache Redis, lock distribuído, retries e timeouts controlados.
- Métricas de cache, provedor, retries e lock disponíveis internamente.
- Alertas ativos do INMET integrados com cache e estados de disponibilidade.
- Busca de localidades com sugestões no frontend.
- Timeout, cancelamento e proteção contra respostas obsoletas.
- Acessibilidade funcional e layout responsivo validados.
- Workflow de CI para build, testes, análise estática, Nginx e smoke test.
- Smoke test da CI compatível com assets hashados gerados pelo Vite.

## Próximas etapas

1. Executar a revisão independente final com evidência por requisito.
2. Sincronizar evidências após essa revisão.
3. Revisar as alterações, criar o commit e publicar `Atualizacao-Geral-V3`.
4. Provisionar `.homolog/` e validar a stack real de homologação.
5. Executar a revisão independente final com evidência por requisito.
6. Definir protocolo e dados para calibrar a política de risco.
7. Consolidar o contrato operacional dos alertas oficiais.
8. Definir, se necessário, identidade, histórico e notificações.
9. Planejar implantação pública, CD, monitoramento e rollback.

O processo de validação offline, com fallback e critérios para aumentar o
escopo da previsão, está descrito em [possível continuação e viabilidade de
escopo](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md).

## Tarefas históricas

O arquivo [tasks.md](../planejamento/evolucao-climaprev/tasks.md) mantém as
25 tarefas do ciclo base, seus gates e a matriz de testes. O arquivo
[Possível Plano de Evolução](PossivelPlanoDeEvolução.md) mantém o backlog
ampliado e as ideias de evolução do produto.

### Incremento espacial — 19/10/2026

Plano espacial congelado em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md e evidence/plano-espacial-2024-2026-10-19.json: 72 snapshots previstos, com controle municipal novo e braço nas coordenadas INMET de 2024, altitude e seleção de célula fixas por par. Sete testes novos aprovados, mypy aprovado. Coletor, preflight do provedor, coleta e comparação ainda pendentes; nenhum resultado espacial ou ganho de previsão declarado. Mantidos reference-v1 ativa e bloqueio de fitting/etapa 6.

### Execução espacial concluída — 19/10/2026

O incremento espacial anterior avançou: coletor e pareamento implementados, preflight real aprovado, 72 snapshots coletados sem falhas, 180 estratos e 30 agregações comparados, sem perda adicional dos dias elegíveis anteriores. Os resultados são mistos; nenhuma detecção dos altos de chuva horária/diária/rajada foi recuperada e a temperatura mínima teve MAE maior nos três horizontes. Reference-v1 mantida, sem fitting ou promoção. Próximo incremento: catálogo dos casos altos perdidos e falsos alarmes, seguido de consolidação dos limites e critérios científicos. Detalhes e evidências em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md. As pendências de coletor/coleta citadas no registro anterior estão concluídas.

### Catálogo e diagnóstico — 19/10/2026

Catálogo espacial concluído com 3.747 casos e reconciliação dos 180 estratos; valores, classes moderada/alta, margens aos limiares, ambos os braços/fontes e hashes preservados. Altos observados concentrados em seis unidades local/data; não recuperados por GFS ou ERA5. Consulta na estação melhora detecção de calor moderado, mas aumenta falsos alarmes. 85 testes direcionados aprovados, Ruff e mypy do módulo novo aprovados. Dois subagentes fizeram revisões independentes read-only de integridade/resultados e pendências científicas. Diagnóstico/adendo em docs/planejamento/reference-candidate-1/diagnostico-e-adendo-2026-10-19.md. Próximos: diagnóstico horário nos dados existentes, auditoria de reservas e decisões científicas; fitting/etapa 6 continuam bloqueados.

### Diagnóstico horário e inventário local — 19/10/2026

Concluídos diagnóstico de 37 registros relevantes para alto, com perfis e recompostos conferidos, e inventário local de reservas: 114 snapshots conhecidos, 14 artefatos de testes, zero origem desconhecida e zero correspondência conhecida com períodos reservados. Isso não certifica independência das reservas nem ausência de acesso externo/anterior. 88 testes direcionados aprovados; Ruff e mypy do módulo temporal aprovados. Versões iniciais preservadas; evidências atuais com sufixo v2. Detalhes em docs/planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md. Próximos: revisão científica e proveniência, critérios de aceite e protocolo prospectivo final; etapa 6 bloqueada. Nenhuma alteração no PDF acadêmico.

### Desacoplamento de implantação — 20/10/2026

Frontend com contexto Docker/Nginx/Compose/documentação próprios; API origin configurável no build, CSP restrita e sem proxy app no modo externo. API com Compose próprio e CORS JSON/headers expostos configurados. Modo integrado preservado; CI/homologação atualizadas. Verificações: 18 testes frontend e 37 API/segurança, build/typecheck/lint/Ruff/mypy, Composes e Nginx sem rede com HTTP 200 aprovados. Navegador end-to-end/domínios reais permanecem pendentes. Detalhes em docs/arquitetura/desacoplamento-2026-10-20.md e RELATORIO-PENDENCIAS-2026-10-20.md. Monorepo preservado; nenhuma publicação ou alteração científica.

### Desacoplamento validado em navegador — 20/10/2026

Concluído o escopo técnico local de separação: gate HTTPS no Edge com frontend/API em origens distintas, busca/POST/resultado via API real, 503, 429 com headers e cooldown, origem bloqueada e interface disponível com processo da API parado. Apenas upstream meteorológico sintético. TLS: cadeia/hostname verificados com CA explícita; navegador com pin SPKI restrito ao processo, sem trust global. Evidência em docs/operacoes/evidence/desacoplamento-browser-2026-10-20.json; reprodução em tests/docker/decoupling/README.md. Modo integrado regressivo aprovado nos gates estático/HTTP/proxy. Job de CI configurado, execução remota e produção não afirmadas. Bancada isolada encerrada. Sem separação de repositórios, publicação ou alteração científica.

### Datas/fusos atuais e horizonte futuro — 20/10/2026

Correção técnica da janela atual concluída: sete datas inclusivas de hoje UTC até +6, API GET/POST rejeita fora da janela antes do serviço e UI informa/atualiza limites na virada de dia e retorno ao foco. Dias meteorológicos mantêm fuso local. 618 testes backend e 20 frontend aprovados, build/typecheck/lint/Ruff/mypy, gate HTTPS com calendário/422 e smoke integrado aprovados. Fixtures isoladas de hosts do Compose e relógios DST, sem remover proteções reais. Ampliação para 14 datas com sete dias por consulta apenas registrada no RDP, não ativada por orientação do usuário. Detalhes em docs/arquitetura/datas-e-fusos-2026-10-20.md. Próximas frentes técnicas: validade/cobertura de alertas e prazo global de consulta; decisões científicas seguem pendentes.


### Encerramento técnico local das frentes — 20/10/2026

Alertas com validade/cobertura conservadoras, prazo cooperativo global de 7 s, interface com contexto/foco/idioma reativos, CI ampliada, exporter privado por worker e carga local implementados. Validação: 644 testes backend e 27 frontend, build/tipagem/lint/actionlint e imagem runtime UID 10001 sem ferramentas de desenvolvimento aprovados. Cinco cenários de carga: 3.000 requisições, zero falhas, cerca de dez req/s, maior p95 580 ms; sem alegação de capacidade de produção. INMET real não confirmado (erro de protocolo), CI remota não executada e monitoramento externo não instalado. Hospedagem/publicação adiadas expressamente pelo usuário; não priorizar infraestrutura. Reference-v1 e janela atual de sete datas preservadas; 14 dias apenas planejado e decisões científicas independentes continuam pendentes. Detalhes e evidências: docs/operacoes/execucao-frentes-1-a-7-2026-10-20.md e RELATORIO-PENDENCIAS-2026-10-20.md. PDF acadêmico preservado.
