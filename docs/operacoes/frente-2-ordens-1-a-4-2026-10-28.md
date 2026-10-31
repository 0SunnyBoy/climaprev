# Frente 2 — Execução das ordens 1 a 4

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Data: 28/10/2026. Escopo autorizado: continuar protocolo, equivalência, controle D+7 e critérios. Não inclui executar campanha, refinar pesos, ler novos resultados reservados ou integrar/promover a candidata.

## Ordem 1 — Protocolo

Preparado o [quadro de parâmetros em JSON](../planejamento/reference-candidate-1/frente-2-protocolo-proposto-2026-10-28.json), complementar ao [protocolo para revisão](../planejamento/reference-candidate-1/frente-2-protocolo-revisao-2026-10-27.md). Separa direção aceita, propostas numéricas e decisões ainda ausentes. Não é configuração de execução nem entrada do runner.

Chuva diária D+1 e direção inicial de redução de pelo menos 5% no MAE permanecem. Três estações, piloto de 14 dias, confirmação de 12 meses, margem de 0,5 mm/dia, tolerâncias de cinco pontos percentuais, confiança de 95% e bloco inicial de sete dias continuam propostos. Cobertura mínima, suporte, datas, partições, instrumento e horários/rodadas não foram inventados para preencher lacunas.

**Conclusão da ordem:** preparação documental e representação estruturada entregues; fechamento científico continua pendente de revisão/aceite e dos parâmetros ausentes.

## Ordem 2 — Equivalência

O diagnóstico de contratos foi ligado ao pareamento experimental de chuva (`pair_station_rain`). Valores, unidades, semântica e duração incompatíveis retiram o valor previsto do conjunto elegível, com causas explícitas em `measurement_contract_exclusions` e `exclusions`. Falta de observação continua sendo falha de cobertura observacional, separada do contrato da previsão.

Para previsão de seis horas, a observação é somada no intervalo exato a partir de horas realmente existentes e completas. Não há divisão artificial da previsão em seis valores horários. Um intervalo que cruza o limite do dia continua inelegível segundo o agregador existente.

Os contratos de temperatura, rajada e umidade permanecem disponíveis como diagnóstico isolado; o pareamento multivariável completo é trabalho posterior. Equivalência de instrumento, altura, representatividade de grade e antecipação da rodada não é demonstrada pelo verificador. O importador de estação não ganhou campos instantâneos de temperatura/umidade nesta entrega.

A identidade do pipeline agora inclui o módulo de equivalência do qual o pareamento depende. Manifestos anteriores não são alterados: se seus hashes não corresponderem, precisam de nova preparação explícita; não os regenerar silenciosamente.

**Conclusão da ordem:** integração técnica de chuva entregue; elegibilidade científica completa e extensão às demais variáveis continuam parciais.

## Ordem 3 — D+7

Cada estrato do comparador passa a expor o controle selecionado e um estado: `absent`, `no_common_eligible_cases` ou `exploratory_paired_cases`. A referência declarada `operational-baseline` é diferenciada de referências experimentais entre modelos. Essa identificação não autentica a proveniência do arquivo.

D+7 sem baseline continua visível, sem score em casos comuns. Uma referência alternativa entre modelos não passa a ser chamada de baseline pública. Nenhum estrato declara superioridade da candidata sobre a reference-v1. Os horizontes atuais continuam etiquetas em dias após coleta, não antecedência de rodada comprovada.

**Conclusão da ordem:** tratamento técnico e recomendação preparados. A proposta de usar comparação secundária exploratória em D+7 ainda precisa de aceite; a janela pública permanece hoje UTC até +6.

## Ordem 4 — Critérios de avaliação

Novo módulo `experimental_criteria.py`, sem limites quantitativos padrão: `RainCriteria` exige valores explícitos e `RainEvidence` recebe evidências para `evaluate_rain_criteria`.

Entradas incluem ganho relativo e absoluto mínimo de MAE, cobertura comum mínima sobre os casos planejados, pares e eventos mínimos, confiança e margens de detecção/falsos alarmes. Ganho de MAE é avaliado com intervalo pareado da diferença candidata menos baseline; detecção usa o limite inferior dessa diferença e falsos alarmes o superior. Margens de detecção/falsos alarmes são frações, não números percentuais inteiros.

- `met`: evidência declarada suficiente e critérios fornecidos atendidos.
- `not_met`: evidência declarada suficiente, mas pelo menos um critério não atendido.
- `inconclusive`: faltam casos idênticos, independência declarada, suporte, cobertura, métricas ou incerteza compatível. Falhas diagnósticas já observadas também permanecem listadas.

Mesmo `met` mantém `scientific_approval=False` e `promotion_allowed=False`. O módulo não verifica por si só se a independência, a metodologia dos intervalos ou o protocolo foram realmente respeitados. Não é motor de aceite humano. Seus limites de teste são sintéticos e não aprovam cobertura ou suporte da campanha.

O módulo consome intervalos já calculados; não implementa o cálculo de incerteza da ordem 6, não executa refinamento da ordem 7 e não está ligado à promoção da aplicação. Sem intervalos válidos a estimativa pontual favorável não é suficiente. Baseline com MAE zero torna o ganho relativo indefinido e a análise inconclusiva.

**Conclusão da ordem:** contrato e avaliador diagnóstico entregues; valores finais e evidência confirmatória seguem pendentes.

## Limites de continuidade

As ordens 1 a 4 avançaram no escopo técnico possível sem presumir aprovações científicas. Não foram declaradas integralmente encerradas. Parar aqui nesta rodada: não ampliar comparador multivariável (ordem 5), implementar inferência de incerteza (ordem 6), ajustar candidata ou executar confirmação/integração.

A próxima decisão humana é revisar o quadro de parâmetros e registrar o que será aceito ou ajustado, começando por locais e piloto. As decisões não podem ser inferidas da autorização geral para continuar a implementação.

## Verificação

Suíte completa em Docker com Redis de testes isolado: **815 testes aprovados em 58,96 s**, warnings como erros. Mypy Linux em **85 módulos** e Ruff em src/tests aprovados. Cenários sintéticos cobrem ganho pequeno, falta de suporte/cobertura/independência/incerteza, baseline zero, regressão de extremos, valores inválidos, contratos incompatíveis, acumulação exata de seis horas e ausência de controle D+7. Nenhum ganho real novo foi calculado.

Alterações locais sem commit/push. Não houve alteração de frontend ou contrato público, migração de repositório ou implantação. Os resultados remotos anteriores não qualificam este diff.
