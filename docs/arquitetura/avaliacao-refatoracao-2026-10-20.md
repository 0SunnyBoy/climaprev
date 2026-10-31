# Avaliação de refatoração — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Atualização posterior: parte das recomendações foi implementada por autorização do usuário. Ver [execução da refatoração](../operacoes/refatoracao-2026-10-20.md). O parecer abaixo registra o diagnóstico anterior; a afirmação de nenhuma implementação ao final se refere àquele momento.

## Parecer

Recomenda-se refatoração incremental antes de ampliar a execução para múltiplas fontes. Não há justificativa identificada para reescrever a aplicação, trocar frameworks, criar microserviços ou separar repositórios. Domínio com dataclasses, portas Protocol, adaptadores HTTP e componentes Vue já oferecem limites úteis. Refatorar melhora manutenção e reduz risco de evolução; não comprova ganho de velocidade ou precisão meteorológica.

Escopo: leitura estática do código atual, incluindo as modificações locais da etapa de responsividade. Não foi feita mudança funcional nesta avaliação, nova execução de testes ou consulta ao CI. As validações anteriores não certificam uma refatoração futura. A análise não constitui auditoria exaustiva de defeitos.

## Achados e sequência recomendada

| Ordem | Evidência | Alteração proposta | Benefício e risco |
|---|---|---|---|
| 1 | `frontend/src/composables/useRiskQuery.ts` e `useLocationSearch.ts` repetem AbortController, sequência, Promise.race, timeout e cleanup | Extrair utilitário pequeno para prazo/cancelamento da operação. Manter debounce e estados reativos nos composables. Preservar erros específicos e prazos 5/10 s | Evita corrigir corridas duas vezes. Risco moderado: cancelamento e timeout têm semânticas diferentes; não criar um composable genérico que esconda essa distinção |
| 2 | `src/climaprev/api/routes/risk.py` declara modelos Pydantic e conversão da resposta junto com handlers; `api/schemas/risk.py` contém entrada | Separar schemas de saída e mapper HTTP das rotas. Manter nomes públicos/OpenAPI, status, unidades e envelope | Facilita manutenção de contrato. Preservar referências/imports usados pelos testes e consumidores; testar equivalência do OpenAPI |
| 3 | `application/services/forecast_query.py` concentra DTOs, codecs de cache, conversões Celsius/Fahrenheit, combinação de risco, geocodificação, cache, lock/heartbeat e alertas | Extrair primeiro DTOs/transformações puras e codecs, com dependências em um sentido; depois um serviço de alertas e um componente de recuperação de previsão. Manter ForecastQueryService como orquestrador | Principal ganho de coesão. Risco alto se cache/lock/expiração forem alterados junto; preservar ordem, TTLs, chaves, fallback, cleanup e exceções |
| 4 | Métrica de erro no serviço e `request.state.provider` na rota usam literal `open-meteo`; chave de previsão inclui URL, normalização e perfil, sem identidade explícita do modelo/rodada | Preparar identidade tipada de provedor/modelo e configurar métricas no ponto de composição; especificar nova identidade de cache antes de integrar novos modelos | Necessário para rastreabilidade de múltiplas fontes. Ausência de modelo/rodada é lacuna para a expansão, não colisão comprovada no uso atual. Mudança de contrato/cache é evolução funcional separada, não extração neutra |
| 5 | `frontend/src/services/api.ts` mantém transporte, erros e validação manual extensa; tipos TS são mantidos separadamente dos schemas Python | Separar validação de payload e transporte. Avaliar geração de tipos pelo OpenAPI e um gate de divergência; preservar validação em runtime | Reduz divergência ao adicionar campos/fontes. Tipos gerados não validam JSON em execução. Não compartilhar implementação Python com navegador |
| 6 | `application/ports.py` define `RiskPolicy = Any` em TYPE_CHECKING; testes de prazo importam fixtures de um módulo de teste de integração | Usar tipo RiskPolicy real sob TYPE_CHECKING quando compatível; mover doubles/fixtures reutilizados para suporte de testes | Melhora tipagem e independência dos testes. Menor prioridade; não precisa adiar a candidata por organização cosmética |

## Divisão sugerida do serviço

- `ForecastQueryService`: resolver caso de uso, executar avaliações e montar resultado da aplicação.
- DTOs/mapper da aplicação: conversão de unidades e estruturas independentes de FastAPI.
- Codecs de cache: ler/escrever a representação persistida sem alterar formato neste primeiro passo.
- Recuperação de previsão: fresh/stale, lock, heartbeat, falha e expiração.
- Consulta de avisos: cache próprio, falhas conservadoras, seleção temporal e validade na entrega.

Os nomes e caminhos novos devem seguir o grafo real de dependências durante a implementação. Não criar camada abstrata para cada função; extrair por responsabilidade, mantendo funções puras quando bastarem. O limite de fuso entre coordenadas, previsão e avisos merece regressão explícita antes de qualquer paralelismo.

## Critérios para executar

1. Registrar o diff local já validado antes de misturar novas extrações. Commit/push não foram executados nesta avaliação.
2. Fazer lotes pequenos: cancelamento frontend; schemas/mapper; DTOs/codecs; recuperação/alertas; identidade de fontes em mudança funcional própria.
3. Em cada extração, preservar payloads, datas, unidades, qualidade, política reference-v1, status de alertas, chaves/TTLs e comportamento de falha/cancelamento. Não promover a candidata.
4. Usar testes existentes e acrescentar regressões apenas para contratos ou riscos não cobertos. Frontend: sucesso, falha, timeout, cancelamento, substituição e desmontagem. Backend: cache corrompido/obsoleto, expiração durante entrega, concorrência/heartbeat e avisos.
5. Antes de concluir o lote estrutural, executar suítes pertinentes, tipagem/lint/build, contrato/OpenAPI e gates de CI do commit correspondente quando enviado. Comparar medições com método equivalente se houver promessa de desempenho; tamanho de arquivo não é métrica de qualidade isolada.

## Preservação científica e prioridades

Módulos de experimento contêm fingerprints de algoritmos e snapshots rejeitam divergências sem migração explícita. Não reorganizar código científico ou recalcular evidências históricas como limpeza incidental; verificar o conjunto de arquivos fingerprintados antes de movê-los. Alterações de modelos, pesos, critérios e fontes continuam sendo evolução científica sujeita a desenho e avaliação próprios.

Acessibilidade auditiva continua pendente por indisponibilidade do usuário. Preparação do protocolo e pesquisa de fontes podem prosseguir enquanto se fazem extrações pequenas. A refatoração do backend deve anteceder a integração operacional de várias fontes; não precisa bloquear o desenho científico ou coleta experimental independente. Horizonte de 14 dias e hospedagem continuam adiados.

## Resultado desta avaliação

Recomendação: executar os itens 1–3 em lotes controlados, e tratar o item 4 como requisito da integração de múltiplas fontes. Itens 5–6 entram conforme impacto no próximo contrato. Nenhuma refatoração implementada nesta revisão; somente diagnóstico documentado.
