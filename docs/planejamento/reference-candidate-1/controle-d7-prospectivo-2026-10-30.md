# Controle D+7 — desenho prospectivo separado

> **Atualização de implementação:** [infraestrutura D+7 e refatoração](../../operacoes/refatoracao-controle-d7-2026-10-30.md) implementadas após esta especificação/revisão; execução desativada. O texto original abaixo preserva o estado preparatório, inclusive o coletor ainda não implementado naquele checkpoint. Altura, calibração e representatividade individuais continuam sem comprovação.

## Decisão e escopo

Usar uma **nova versão do controle baseado no adaptador de produção e política reference-v1**, com alvo D+7, arquivamento e identidade próprios. Este documento conclui a especificação preparatória; não implementa nem ativa um coletor. [Plano estruturado](controle-d7-prospectivo-2026-10-30.json).

A janela pública 14/7 já aceita D+7. O coletor experimental `collect_baseline` mantém intencionalmente o intervalo congelado hoje..+6. Sua mensagem sobre janela pública descreve o contrato antigo: não é a elegibilidade atual da API. A ausência de controle D+7 no piloto existente permanece explícita.

Não editar esse coletor, seus arquivos, manifests, cota, E1 ou ledger para acomodar o controle novo. A nova série não contará entre as 210 capturas do piloto v5 nem substituirá arquivos existentes. Sem backfill, mistura de versões ou leitura de resultados reservados.

## Definição temporal e população

- Pontos: coordenadas verificadas de A201, A001 e A801, com versão do catálogo registrada.
- Slot proposto: 18:00 UTC, prazo de 30 minutos, apenas em datas futuras explicitamente congeladas em calendário próprio. Usar relógio UTC com offset; não escolher horário após observar desempenho.
- Para cada estação, `target_date = data_local(slot) + 7 dias`. Alvo diário: meia-noite local da data até meia-noite local seguinte, convertido para UTC; horário final exclusivo. D+7 é antecedência em dias civis, não exatamente 168 horas até o início do alvo.
- Exemplo aritmético, **sem reserva ou captura criada**: slot 31/10/2026 18 UTC nas três zonas atuais → alvo 07/11, intervalo 07/11 03 UTC até 08/11 03 UTC; antecedência até o início 153 horas. Usar ZoneInfo, sem fixar UTC−3 como regra universal.
- Solicitar um dia (`start_date = end_date = target_date`), dentro da janela pública 14/7. A série horária deve cobrir todos os intervalos que compõem esse dia, inclusive o endpoint da última hora. Resposta diária disponível não prova cobertura horária completa.

## O que o controle representa

Reutilizar o comportamento do adaptador Open-Meteo e os limiares da reference-v1, com novas identidades de controle e implementação. Seleção automática continua `unknown_auto_selection`; não inventar rodada ou modelo. Comparação é por disponibilidade no mesmo slot, não por mesma inicialização.

Escopo: adaptador e política, **sem reproduzir cache, geocodificação, avisos oficiais ou o fluxo completo da API pública**. Registrar ponto solicitado e ponto/célula retornado separadamente; proximidade de coordenadas não certifica representatividade. Atualizações do provedor ao longo do estudo permanecem limitação.

## Arquivo, elegibilidade e falhas

Antes de executar: calendário completo, protocolo próprio, autorização/registro de coleta aplicável, orçamento de chamadas compartilhadas por provedor e bloqueio de partições precisam estar válidos. Não supor que nova pasta elimina o limite de chamadas do piloto.

Guardar corpo original da resposta de previsão em bytes, parâmetros, URL sem segredos, horário real de envio/obtenção, status HTTP, estação, alvo, fuso, unidades, modelo/rodada declarados ou desconhecidos, versões do adaptador/política/normalizador e hashes. Snapshot normalizado e saída de risco são derivados separados. O coletor congelado atual não garante todos esses itens; isso é requisito da futura implementação.

Identidade única: protocolo/controle, estação, slot e alvo; impedir duplicidade e reabertura silenciosa de falha. Ledger e arquivos próprios, distintos do piloto. Captura fora da janela, após início do alvo, fora do ponto/versão esperado, sem integridade ou com cobertura incompleta fica excluída, com motivo registrado. Ausência de D+7 em um modelo não elimina seu slot planejado do denominador e não é preenchida por outra fonte.

Observação: CSV oficial preservado e ligado à estação por proveniência, unidades e intervalos verificados; soma exata das horas do dia local. Não imputar zero, interpolar observação ou substituir medição por reanálise. Manter métricas indefinidas quando não houver pares suficientes.

## Avaliação e separação científica

D+7 permanece **secundário exploratório**, separado do objetivo primário chuva D+1. Comparar chuva diária por pares elegíveis, relatar MAE, diferença pareada, cobertura de cada braço e pares comuns; extremos e incerteza com suporte explícito. Não converter concordância entre modelos em probabilidade de acerto. Séries históricas sem controle D+7 não ganham comparador retroativo.

O novo controle só compara com previsões também capturadas prospectivamente no mesmo desenho/slot e partição. Caso seja indispensável alterar a coleta congelada, planejar uma campanha sucessora, nunca uma migração silenciosa do v5 ativo. Datas concretas e dimensionamento serão congelados antes dos novos resultados; esta especificação não cria campanha confirmatória ou cota nova.

Manter embargo temporal, conjuntos de desenvolvimento/seleção/confirmação separados, plano de multiplicidade e critérios fixados antes da confirmação. Reposições ou atrasos que cruzem partições exigem replanejamento prospectivo; nunca deslocar limites para melhorar métricas. Nenhuma promoção é autorizada por este desenho.

## Implementação futura e critérios de conclusão

1. Implementar coletor sucessor de D+7 com resposta bruta rastreável, normalização e política versionadas, sem modificar a automação ativa.
2. Implementar ledger/manifesto próprios e coordenação do orçamento total com quaisquer coletores simultâneos.
3. Testar UTC/fuso/virada de data, corte 14/7, endpoint horário final, ausência de dados, duplicidade, corrupção de arquivo, coleta tardia e divergência de versão.
4. Verificar prospectivamente disponibilidade D+7 por braço/estação; arquivar diagnóstico separado, sem contar como amostra de avaliação.
5. Congelar calendário, partições, critérios e autorização de execução próprios; só então coletar e avaliar. Ganho de precisão e eventual promoção dependem de evidências posteriores.

[Metadados instrumentais](metadados-instrumentais-2026-10-30.md) · [Janela pública](../../operacoes/horizonte-14-consulta-7-2026-10-30.md) · [Manual do piloto preservado](../../operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md).
