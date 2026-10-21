# ROADMAP — ClimaPrev

## Ordem vigente

O [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) mantém a lista detalhada e o [STATE](STATE.md) registra o que foi validado. Não repetir aqui contagens ou SHAs de execução.

1. Responsividade local: concluída; acompanhar provedores e regressões. Refatoração transversal/limpeza concluída no lote local, antes de integrar várias fontes.
2. Acessibilidade auditiva: ensaio manual pendente por indisponibilidade do usuário; não substituído por teste automatizado.
3. Fechar desenho científico, adequação de variáveis, independência de reservas, métricas e critérios com o usuário responsável pelo aceite.
4. Selecionar fontes/modelos e confirmar cobertura, histórico, licença e uso comercial.
5. Coletar/normalizar previsões experimentais com origem, rodada e antecedência rastreáveis, preservando dados de avaliação.
6. Comparar cada modelo e combinações com observações, por variável, cidade e horizonte.
7. Refinar candidate-1 com ganho demonstrado fora dos dados de ajuste.
8. Integrar candidata qualificada com rastreabilidade, falhas explícitas e desempenho verificado; promoção não automática.
9. Definir distribuição aberta, licença e escopo de serviços comerciais, autenticação/quotas e suporte quando aplicável.

## Critérios transversais

Preservar contrato, política reference-v1 e integridade dos dados. Validar cada mudança com testes/checks apropriados; conferir CI e Security gates do SHA enviado antes de merge. Propostas e bons resultados locais não aprovam produção ou precisão científica.

Hospedagem, monitoramento no ambiente definitivo e horizonte de 14 dias continuam adiados. Separação de repositórios não faz parte desta execução. [Histórico](ROADMAP-HISTORICO-ATE-2026-10-20.md).
