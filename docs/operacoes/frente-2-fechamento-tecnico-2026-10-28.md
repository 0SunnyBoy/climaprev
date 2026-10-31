# Frente 2 — preparação do fechamento técnico

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Escopo autorizado

Em 28/10/2026, o usuário pediu avançar na frente 2 antes da disponibilidade dos dados necessários. A interpretação adotada é concluir ferramentas e preparação primeiro e realizar a validação empírica depois, com as entregas da frente 1. Não equivale a comprovar qualidade, encerrar a confirmação ou promover a candidata.

## Incremento entregue

`src/climaprev/tools/experimental_uncertainty.py` liga a reamostragem histórica por blocos de datas ao diagnóstico de critérios de chuva. Recebe pares observação/baseline/candidata de uma única experiência e antecedência, denominador planejado, limiar de evento e parâmetros explícitos. Não lê dados reservados, consulta provedores ou ajusta modelos.

- Calcula diferenças candidata menos baseline de MAE, detecção e razão de falsos alarmes (falsos alarmes/eventos previstos).
- Agrupa estações da mesma data; separa lacunas do calendário e expõe blocos curtos, estimativas degeneradas e repetições sem suporte.
- Mantém intervalos ausentes quando não são calculáveis; ausência de eventos não vira taxa zero.
- Ordena os pares, rejeita duplicação estação/data e valores inválidos; registra hash dos pares, seed, suporte e parâmetros.
- Preserva cobertura contra o calendário planejado e encaminha intervalos ao avaliador existente.
- Não certifica elegibilidade, proveniência ou independência. O diagnóstico mantém independência não estabelecida e não autoriza promoção, mesmo com melhora sintética.

Os intervalos são exploratórios e marginais. A implementação não resolve seleção do tamanho de bloco, múltiplas comparações, suficiência amostral, representatividade ou independência meteorológica. Um intervalo estreito em teste sintético não valida o método para a campanha. O módulo ainda recebe pares explicitamente; a ligação automática aos arquivos integrados e às partições não está concluída.

## Verificação

46 testes específicos aprovados com warnings como erros: novo módulo, bootstrap existente e critérios. Ruff dos arquivos novos e mypy do módulo aprovados. A execução ampliada em Windows não foi qualificada nesta rodada; não transferir a aprovação remota de 858 testes do commit anterior para este incremento. Arquivos locais, sem commit/push nesta rodada.

## O que ainda precisa ser preparado sem os dados novos

1. Consumir os relatórios de pareamento com validação de identidade, elegibilidade, fonte e partição, evitando que dados arbitrários recebam aparência de evidência auditada.
2. Gerar diagnósticos por estação/antecedência, sensibilidade de blocos e plano de multiplicidade antes de qualquer uso confirmatório.
3. Preparar alternativas de refinamento e seleção apenas para desenvolvimento, com rastreabilidade de ajustes e congelamento. Não escolher pesos sem dados.
4. Preparar relatório final e gate de integração condicionado à evidência e ao aceite.

## O que depende dos dados e permanece aberto

Observações recentes, equivalência instrumental não resolvida, execução do piloto, suporte efetivo para extremos, escolha fundamentada do bloco, ajuste e seleção de variantes, congelamento efetivo e confirmação independente. Integração pública depende de resultado favorável e decisão final. Reference-v1 permanece ativa; sem ganho real calculado.

Não marcar F2-06 a F2-09 como concluídas. F2-06 recebeu uma primeira ligação técnica; a frente 2 ainda não está tecnicamente encerrada.
