# Implementations and refactoring

**Publicação e qualificação em 20/10/2026:** atualização enviada à develop; lote funcional `f0eab5e` aprovado em CI e Security gates. As correções de imagem/CSP passaram remotamente. Não houve merge em main ou deploy. Estado e pendências vigentes no [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md); descrições de alterações não enviadas/CI pendente abaixo pertencem aos lotes anteriores.

## Atualização vigente — 20/10/2026

Versão 0.1.0 de backend/frontend em desenvolvimento, branch develop na base 23bf4ce, com alterações sem commit/push. O [STATE](STATE.md) consolida implementações e evidências; o [RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md) define pendências.

Concluídos localmente: desacoplamento, janela UTC de sete datas, validade/cobertura conservadora de avisos, prazo global cooperativo, interface revisada, CI configurada, métricas por worker e campanha de carga. 644 testes backend e 27 frontend, checks estáticos/build e gate HTTPS aprovados; 3.000 requisições locais sem falhas. Resultados não aprovam produção ou candidata científica.

Ordem atual: (1) INMET real; (2) revisão/publicação do diff quando autorizada e CI remota; (3) revisão científica preparatória; (4) critérios de aprovação; (6 da lista original) acessibilidade manual. Por último, evolução da candidate-1 focada explicitamente em qualidade e precisão da previsão. Reference-v1 preservada; nenhum ajuste/calibração/promoção. Horizonte de 14 dias só planejado. Hospedagem adiada; monorepo mantido; não atualizar PDF acadêmico.

GitHub: CI da base passou; Security gates falhou no teste de tema. Correção local ainda sem rerun remoto; develop sem proteção/checks obrigatórios. Preservar alterações acumuladas, não incluir segredos/.homolog/dados brutos/artefatos locais no envio. Protocolos e evidências congelados não devem ser reescritos.

## Histórico

Os registros anteriores estão no [arquivo histórico](ImplementationsAndRefactoring-HISTORICO-ATE-2026-10-20.md). Eles não redefinem as prioridades ou o estado vigente.


## Catálogo técnico vigente

| Componente | Implementação local | Verificação / limitação |
|---|---|---|
| Frontend | Docker/Compose/Nginx próprios, origem API validada, CSP e consumo HTTP | Build independente; API pode estar parada sem impedir servir a interface |
| API | Compose API/Redis próprio, CORS/hosts, request ID e Retry-After | Contrato HTTP mantido; tipos TS/Python separados |
| Datas | `api/forecast_window.py` e utilitário frontend | Hoje UTC até +6; 422 antes do serviço; 14 dias não ativo |
| Alertas | Adaptador inmet-alerts-v2, validade/intervalo local, Polygon/MultiPolygon/furos | Testes sintéticos aprovados; feed real ainda não homologado |
| Cache de avisos | Identidade versionada e reavaliação de expiração antes da entrega | Falha/invalidade não vira ausência de avisos |
| Consulta | `query_total_timeout_seconds`, padrão 7 s/máximo 8 s | Cancelamento cooperativo e cleanup; cliente 10 s |
| UI | Foco/contexto na emergência, teclado/ARIA, erros PT/EN reativos, tema e responsividade | 27 testes e gate automatizado; leitor de tela manual pendente |
| CI | Jobs de validação/runtime/HTTPS, frontend checks e auditoria | Revisão local sem execução remota; Security antigo falhou no tema |
| Métricas | `metrics_store.py`, snapshots por worker e exporter privado Prometheus | Opt-in; lease 20 s; templates sem stack de monitoramento instalada |
| Carga | Cenários UTC, mock de avisos explícito e campanha com limites de recursos | 3.000 requisições/zero falhas localmente; não capacidade de produção |
| Ciência | CSVs oficiais, bootstrap, baseline, comparação espacial, catálogo e diagnóstico horário | Preparação concluída tecnicamente; sem candidata calibrada/promovida ou ganho comprovado |

Ver [execução técnica](../operacoes/execucao-frentes-1-a-7-2026-10-20.md) para tempos, cenários e limites, e [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) para pendências.
