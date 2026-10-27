# ROADMAP — ClimaPrev

## Ordem vigente

O [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) mantém a lista detalhada e o [STATE](STATE.md) registra o que foi validado. Não repetir aqui contagens ou SHAs de execução.

1. Responsividade local: concluída; acompanhar provedores e regressões. Refatoração transversal/limpeza concluída no lote local, antes de integrar várias fontes.
2. Acessibilidade auditiva: ensaio manual pendente por indisponibilidade do usuário; não substituído por teste automatizado.
3. Direção científica aprovada em 23/10; fechar parâmetros de campanha, equivalência instrumental, margens e independência dos dados. [Proposta concreta](../planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md).
4. Catálogo e preflight pontual de quatro fontes/modelos em três pontos realizados; fechar identidade de rodada, qualidade e seleção final. [Preflight](../operacoes/coleta-experimental-2026-10-23.md).
5. Arquivo, coletores, normalização inicial, baseline por adaptador/política, rodada explícita, manifesto/ledger local e pareamento exploratório de chuva implementados. [Entrega de 26/10](../../RELATORIO-IMPLEMENTACAO-2026-10-26.md). Fechar desenho, controle de D+7, equivalência das outras variáveis e acionador antes da campanha; runner permanece desativado.
6. Comparador exploratório de chuva, baseline diária e elegibilidade implementados; integrar calendário à cobertura global, completar outras variáveis e inferência estatística após fechar o protocolo. [Entrega](../operacoes/comparacao-experimental-2026-10-26.md). Sem novo ganho real calculado ou promoção.
7. Refinar candidate-1 com ganho demonstrado fora dos dados de ajuste.
8. Integrar candidata qualificada com rastreabilidade, falhas explícitas e desempenho verificado; promoção não automática.
9. Definir distribuição aberta, licença e escopo de serviços comerciais, autenticação/quotas e suporte quando aplicável.

## Critérios transversais

Preservar contrato, política reference-v1 e integridade dos dados. Validar cada mudança com testes/checks apropriados; conferir CI e Security gates do SHA enviado antes de merge. Propostas e bons resultados locais não aprovam produção ou precisão científica.

Hospedagem, monitoramento no ambiente definitivo e horizonte de 14 dias continuam adiados. Separação de repositórios não faz parte desta execução. [Histórico](ROADMAP-HISTORICO-ATE-2026-10-20.md).
