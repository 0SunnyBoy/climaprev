# Diagnóstico consolidado e adendo técnico — 19/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Identificador: `reference-candidate-1-preparation-addendum-2026-10-19-v1`.

Este adendo registra retrospectivamente implementações e resultados da preparação. Não substitui o protocolo congelado de 16/10, não constitui aprovação científica e não altera autorização, partições ou critérios após observar resultados. A reference-v1 permanece ativa; fitting, calibração e promoção continuam bloqueados.

## Catálogo auditável

`evidence/catalogo-erros-espaciais-2024-2026-10-19.json` contém 3.747 casos evento/local/data/horizonte, com ambos os braços e GFS/ERA5. Cada caso registra valor observado, classe, previsão, erro numérico, margens aos limiares fixos, detecção de pelo menos moderado e de alto, estação, hash do CSV e hashes dos snapshots. Foram reconstruídas e conferidas as métricas dos 180 estratos contra a comparação espacial anterior, além de verificar o conjunto exato dos 72 snapshots e os parâmetros de cada consulta. O catálogo recusa sobrescrita.

Há 37 registros relevantes para alto em pelo menos uma observação/previsão/controle. Isso inclui falsos alarmes e horizontes repetidos; não são 37 extremos independentes. Os nove extremos observados por evento se concentram em seis unidades local/data:

| Local | Data civil | Evento e valor observado |
|---|---|---|
| Belém | 10/04/2024 | Chuva diária 63,6 mm; máxima horária 31,4 mm |
| Belém | 25/04/2024 | Chuva diária 64,6 mm |
| Belém | 11/07/2024 | Rajada 69,48 km/h |
| Brasília | 02/04/2024 | Chuva diária 70,2 mm |
| Brasília | 14/10/2024 | Chuva diária 59,8 mm; máxima horária 35,2 mm; rajada 68,04 km/h |
| Porto Alegre | 24/10/2024 | Rajada 66,96 km/h |

GFS e ERA5 perdem os altos observados nos dois braços e nos três horizontes. ERA5 é controle diagnóstico, não substituto da estação nem evidência de verdade sobre impactos.

Falsos altos GFS identificados:

| Evento/local/data | Horizonte e braço | Observado | Previsto |
|---|---|---:|---:|
| Chuva diária, Belém, 11/04 | D+3, estação | 12,8 mm | 50,8 mm |
| Chuva diária, Porto Alegre, 07/04 | D+3, ambos | 7,2 mm | 75,5 mm |
| Chuva diária, Porto Alegre, 16/04 | D+1, ambos | 31,0 mm | 61,0 mm |
| Rajada, Porto Alegre, 28/04 | D+7, ambos | 26,28 km/h | 64,8 km/h |

## Efeito sobre eventos moderados

No calor de pelo menos nível moderado, os braços apresentam tradeoff que a MAE isolada não resume. São 29 dias observados por horizonte; resultados GFS municipal → estação:

| Horizonte | Detecções | Falsos alarmes |
|---|---:|---:|
| D+1 | 11 → 27 | 7 → 17 |
| D+3 | 11 → 24 | 5 → 17 |
| D+7 | 11 → 22 | 1 → 12 |

As diferenças de detecção/falsos alarmes de calor entre braços concentram-se em Belém. Não houve alto observado de calor ou frio para avaliar recall alto. Nenhum desses resultados autoriza selecionar automaticamente o braço da estação.

## Limites e encaminhamento

| Questão | Evidência atual | Próxima ação | Estado / responsabilidade |
|---|---|---|---|
| Representação espacial | Coleta pareada concluída, resultados mistos, altos não recuperados | Manter ambos como diagnóstico; não trocar produção | Técnico concluído; interpretação científica pendente |
| Alinhamento temporal | Diagnóstico dos 37 registros concluído e reconciliado com o catálogo | Revisar interpretação científica e diferenças de amostragem; não inferir causa do erro | Técnico concluído; revisão científica pendente |
| Extremos térmicos | INMET registra extremos no intervalo; modelo usa amostras instantâneas | Revisar adequação da comparação antes de propor correção | Revisão científica necessária; responsável não definido |
| Rajada | Semântica de intervalo/amostragem difere entre fontes | Confirmar comparabilidade e qualidade instrumental | Revisão científica necessária; responsável não definido |
| Suporte raro | Seis unidades local/data com altos; calor/frio sem altos | Definir precisão/suporte necessários antes de ampliar coleta | Decisão científica pendente |
| Incerteza | Bootstrap implementado, mas janela de janeiro tem três dias e bloco primário sete | Definir tratamento prospectivo; não remover janeiro retroativamente | Decisão científica pendente |
| Reservas | Protocolo reserva jul–dez/2025 e jan–jun/2026; piloto jan/2025 já conhecido; CSV anual 2025 foi processado estruturalmente | Auditar acessos e artefatos existentes sem abrir outcomes reservados | Independência ainda não comprovada |
| Aceite | Evento/métrica principal, ganho mínimo, tradeoffs, revisor e aprovação continuam nulos no protocolo | Registrar decisões em nova versão antes de fitting | Depende de definição humana/científica |

## Atualização técnica do protocolo

O campo histórico `uncertainty_plan.status=specified_not_implemented` permanece no protocolo original para preservar seu estado congelado. O estado atual é **bootstrap implementado e testado, inferência científica ainda bloqueada pelas condições de suporte/janelas e aprovação**. A coleta espacial também passou de planejada a executada, com manifestos separados do plano prospectivo. Os fingerprints da política e algoritmos estão nos snapshots e baselines; o placeholder histórico do protocolo não deve ser interpretado como ausência desses registros, nem como congelamento científico completo para etapa 6.

Não foi feita nova inspeção de resultados dos períodos reservados neste incremento. Isso não prova inexistência de acesso anterior: a auditoria de proveniência das reservas continua pendente. Não se marca a preparação como cientificamente aprovada.

## Ordem atual — 20/10/2026

Diagnóstico horário e inventário local concluídos, conforme [evidência vigente](diagnostico-horario-e-reservas-2026-10-19.md). Eles não certificam independência das reservas. Revisão científica e critérios seguem prioritários como preparação; fitting/calibração/promoção ficam por último, sem autorização.

## Sequência originalmente proposta — histórica

1. Diagnóstico horário dos casos catalogados usando somente dados existentes de 2024.
2. Auditoria de proveniência das reservas, limitada a metadados, código e artefatos já existentes.
3. Definição científica de fontes, suporte, métricas, ganho mínimo, tradeoffs, multiplicidade e estratos críticos.
4. Nova versão prospectiva do protocolo e congelamento de dados/alvos/código, caso as decisões anteriores permitam encerrar a preparação.
5. A etapa original 6 permanece fora da autorização: não ajustar limiares ou coeficientes, nem promover candidata.

O PDF acadêmico permanece inalterado.
