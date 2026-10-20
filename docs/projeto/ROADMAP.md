# ROADMAP — Clima Prev

## Atualização vigente — 20/10/2026

Versão 0.1.0 de backend/frontend em desenvolvimento, branch develop na base 23bf4ce, com alterações sem commit/push. O [STATE](STATE.md) consolida implementações e evidências; o [RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md) define pendências.

Concluídos localmente: desacoplamento, janela UTC de sete datas, validade/cobertura conservadora de avisos, prazo global cooperativo, interface revisada, CI configurada, métricas por worker e campanha de carga. 644 testes backend e 27 frontend, checks estáticos/build e gate HTTPS aprovados; 3.000 requisições locais sem falhas. Resultados não aprovam produção ou candidata científica.

Ordem atual: (1) INMET real; (2) revisão/publicação do diff quando autorizada e CI remota; (3) revisão científica preparatória; (4) critérios de aprovação; (6 da lista original) acessibilidade manual. Por último, evolução da candidate-1 focada explicitamente em qualidade e precisão da previsão. Reference-v1 preservada; nenhum ajuste/calibração/promoção. Horizonte de 14 dias só planejado. Hospedagem adiada; monorepo mantido; não atualizar PDF acadêmico.

GitHub: CI da base passou; Security gates falhou no teste de tema. Correção local ainda sem rerun remoto; develop sem proteção/checks obrigatórios. Preservar alterações acumuladas, não incluir segredos/.homolog/dados brutos/artefatos locais no envio. Protocolos e evidências congelados não devem ser reescritos.

## Histórico

Os registros anteriores estão no [arquivo histórico](ROADMAP-HISTORICO-ATE-2026-10-20.md). Eles não redefinem as prioridades ou o estado vigente.


## Critérios de encerramento das próximas frentes

| Frente atual | Critério de conclusão |
|---|---|
| INMET | Resposta real verificável, contrato/validade/cobertura validados e comportamento de falha preservado |
| CI | Diff revisado e enviado com autorização; CI e Security aprovados para o mesmo SHA, sem supressão de verificações |
| Revisão científica | Limitações de fontes/amostra e decisão de proveniência/independência documentadas |
| Critérios | Revisor, métricas/evento principal, suporte/ganho mínimo, tradeoffs e protocolo prospectivo definidos antes de ajuste |
| Acessibilidade manual | Evidência com leitor de tela/teclado, PT/EN, foco/erros/resultado/emergência, correções e retestes |
| Candidate-1, ao final | Ganho de qualidade/precisão demonstrado contra v1 em avaliação independente; classificação e valores meteorológicos avaliados separadamente |

Sem prazo de hospedagem definido. Notificações, contas, mapas e oferta comercial da API exigem escopo próprio; não são condições automaticamente adicionadas à entrega atual.
