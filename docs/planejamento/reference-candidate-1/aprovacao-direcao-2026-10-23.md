# Aprovação da direção científica em 23 de outubro de 2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Responsável: usuário solicitante. Registro da manifestação na conversa: **"aprovo a direção tomada"**, após o resumo do protocolo e o esclarecimento de que a avaliação não se limita à chuva.

Status: **direção aprovada; parâmetros finais do experimento pendentes**. Este registro complementa a [proposta de 21/10](proposta-cientifica-para-revisao-2026-10-21.md), preservada como documento submetido à revisão, e não reclassifica como aprovados resultados ou protocolos anteriores.

## Direção aprovada

- Chuva acumulada diária em D+1 como objetivo principal inicial; D+3 e D+7 como avaliações complementares, separadas.
- Temperatura, vento/rajadas, umidade e classificação de risco permanecem no escopo, com métricas e comparabilidade próprias. Ganho em chuva não demonstra melhoria de todas as variáveis.
- Comparação pareada com a previsão operacional atual e observações INMET compatíveis. Comparação dos valores meteorológicos separada da comparação das políticas de risco.
- Meta inicial de redução de pelo menos 5% do MAE no objetivo principal, acompanhada de evidência estatística favorável. É decisão de direção do produto, não norma científica nem demonstração de ganho já alcançado.
- Dados com mesmos locais, datas, unidades e intervalos; ausências não viram zero, exclusões e indisponibilidade devem ser reportadas.
- Teste independente, com campanha prospectiva quando a independência das reservas históricas não puder ser demonstrada; sem ajustar a candidata no teste final.
- Proteção dos extremos e dos estratos críticos: uma melhoria média não autoriza esconder degradação relevante em detecção ou falsos alarmes.
- Resultado inconclusivo quando faltar suporte; integração da candidata depende de evidência e aceite posterior. Reference-v1 permanece ativa.

## Ainda não definido ou aprovado em detalhe

1. Locais, calendário, duração e orçamento da campanha, cobertura sazonal e precisão requerida.
2. Convenções instrumentais finais por variável, fronteiras temporais e critérios de qualidade/cobertura.
3. Redução mínima relevante em unidades físicas, margens para extremos/estratos e custos de omissão versus falso alarme.
4. Partições e identidade dos dados de teste, proveniência/independência das reservas, tamanho de bloco e tratamento de multiplicidade.
5. Modelos/provedores e suas condições de uso; configuração congelada dos braços experimentais.

Esses parâmetros devem ser fixados antes do teste confirmatório, sem seleção pelo desempenho observado. A aprovação de direção não certifica independência das reservas antigas nem autoriza promoção automática, mudança da política ativa ou abertura antecipada de outcomes reservados.

## Próximo trabalho

Detalhar fontes/modelos e o plano de coleta experimental, usando os objetivos aprovados. Preparação de código e pesquisa de fornecedores podem avançar; ajuste confirmatório e decisão de promoção aguardam desenho fechado e resultados qualificados. Não houve coleta, fitting ou alteração da previsão operacional neste registro documental.
