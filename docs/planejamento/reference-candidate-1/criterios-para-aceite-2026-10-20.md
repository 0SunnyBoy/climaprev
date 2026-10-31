# Critérios para deliberação — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

**Proposta, não aprovada. Responsável pelo aceite: usuário solicitante (confirmado na conversa).** Não altera protocolos congelados, não autoriza fitting/calibração/promoção e não muda a reference-v1. A evolução de qualidade/precisão fica por último.

## Condições obrigatórias propostas

1. Fonte observacional, qualidade, unidade, intervalo e dia civil explicitados por variável; temperatura/rajada sem equivalência aprovada não podem sustentar conclusão confirmatória.
2. Mesmos casos elegíveis entre baseline e experimento, exclusões auditadas e sem preenchimento de ausência por zero. Não escolher datas, estação ou braço pelo desempenho observado.
3. Separar melhoria dos valores meteorológicos de melhoria na classificação. Reportar MAE, RMSE e viés em unidades físicas, por variável/local/horizonte; para os eventos, hits, misses, falsos alarmes, detecção, precisão e FAR com denominadores explícitos.
4. Zero eventos observados não permite concluir recall perfeito ou melhoria dos altos. Estratos sem suporte suficiente ficam inconclusivos; acurácia global não substitui avaliação dos extremos.
5. Avaliação confirmatória em dados cuja independência seja aprovada antes da leitura. Dados de 2024 e piloto de Belém jan/2025 continuam exploratórios; reservas antigas não certificadas automaticamente.
6. Intervalos pareados por blocos, respeitando dependência e segmentos, com sensibilidades identificadas como exploratórias. Não remover janeiro nem trocar bloco após observar qual resultado fica favorável.
7. Não promover uma configuração com ganho médio que esconda degradação de estrato crítico. Aprovação exige critérios prévios, proveniência reproduzível, política/perfil separados, fallback v1 e nova autorização de implantação.

## Decisões quantitativas propostas para discussão

Os valores abaixo são **opções de produto a validar**, não resultados inferidos nem recomendações de uma norma meteorológica:

| Decisão | Proposta inicial | O que falta aprovar |
|---|---|---|
| Família de métricas | Valores meteorológicos como objetivo principal; risco como proteção adicional | Selecionar antes da nova avaliação a variável/horizonte principal segundo a necessidade do produto; não escolher pelo melhor resultado de 2024 |
| Ganho mínimo | Considerar redução relativa de 5% do MAE na variável/horizonte principal, acompanhada de diferença pareada favorável | Justificar relevância prática e unidades; 5% é proposta, sem aprovação |
| Extremos | Não aceitar queda de detecção de altos; avaliar falsos alarmes conjuntamente | Definir margem operacional/estatística e custo de omissão versus falso alarme; sem suporte, resultado inconclusivo |
| Incerteza | Intervalos de 95%, mantendo plano pareado e família de comparações pré-definida | Tratamento de multiplicidade, estratos críticos e regra de aprovação |
| Amostra | Planejar pela precisão requerida, taxa de eventos e dependência, sem mínimo arbitrário universal | Precisão tolerada, cobertura regional/sazonal e desenho prospectivo |

Exemplo de planejamento, sem converter em aceite: para estimar uma proporção independente com margem aproximada ±0,10 e 95% no pior caso, n ≈ 1,96² × 0,25 / 0,10² = 97. Esse cálculo não se aplica diretamente a dias correlacionados nem a múltiplos horizontes; não é um requisito universal de 97 dias ou uma prova de poder estatístico. Para recall, o suporte relevante são ocorrências positivas independentes.

## Registro do aceite

O usuário deverá aprovar ou ajustar: convenções das fontes, classificação exploratória/reservada, variável/horizonte principal, ganho mínimo, margens de proteção, precisão/suporte e multiplicidade. Até lá, status `proposed_not_approved`. Aprovar este desenho não autoriza automaticamente ajustar a candidata; essa execução continua adiada.

[Revisão técnica](revisao-preparatoria-2026-10-20.md) · [proposta anterior preservada](baseline-e-criterios-propostos-2026-10-19.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).
