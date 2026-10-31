# Diagnóstico horário e inventário das reservas — 19/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Entregas

O diagnóstico horário cobre os 37 registros relevantes para nível alto do catálogo anterior: 21 de chuva diária, seis de máxima horária de chuva e dez de rajada. São registros evento/local/data/horizonte repetidos, não observações independentes. A evidência vigente é `evidence/diagnostico-horario-2024-2026-10-19-v2.json`.

Para cada caso, foram registrados os 24 valores esperados, horários UTC e locais, todos os empates de máximo, a observação INMET e GFS/ERA5 dos dois braços. As somas/máximos reconstruídos conferem com o catálogo, com tolerância numérica de 0,00001. Os dados de origem não foram modificados e nenhuma data foi deslocada.

A distância entre os endpoints mais próximos de picos empatados varia de 0 a 23 horas nos registros de chuva diária/horária e de 0 a 13 horas nos de rajada, para GFS no braço da estação. Essa medida não informa direção, localização sub-horária ou causa do erro. Em séries planas há muitos picos empatados; distância zero não prova alinhamento físico. Para chuva diária, o horário mostrado é o da maior contribuição horária, não um horário da soma diária. Rajada ERA5 mantém amostragem instantânea; os demais intervalos continuam identificados explicitamente. Não se conclui que corrigir o horário recuperaria os eventos altos.

A primeira evidência temporal foi preservada. A versão v2 foi gerada após ajuste de tipagem sem mudança dos cálculos; contém os fingerprints atuais do gerador e módulo.

## Auditoria local das reservas

O inventário vigente é `evidence/inventario-reservas-2026-10-19-v2.json`. Consultou nomes/tamanhos de arquivos e metadados dos relatórios existentes; não reabriu valores meteorológicos reservados.

- 114 snapshots conhecidos: 42 já registrados na auditoria anterior e 72 da coleta espacial de 2024.
- Nenhum snapshot conhecido ausente ou sem classificação de origem.
- 14 arquivos adicionais identificados como artefatos de testes por localização e código das fixtures correspondentes; não foram tratados como observações meteorológicas.
- Nenhuma correspondência de períodos reservados nos metadados conhecidos: validação jul–dez/2025 e teste jan–jun/2026.

Isso é inventário do estado local atual, não certificação de ausência de acesso anterior. Arquivos removidos, outras máquinas, consultas externas e histórico remoto não foram auditados. O CSV anual de 2025 foi obtido e o parser processa suas linhas antes do filtro de período: há exposição estrutural documentada. O piloto de Belém jan/2025 já examinado continua excluído de qualquer reserva inédita. Não se deve afirmar que as reservas são seguramente inéditas sem revisão de proveniência.

A primeira versão do inventário registrou 14 itens desconhecidos. A revisão dos nomes e das fixtures identificou esses itens como saídas de testes; a versão v2 registra essa classificação sem examinar outcomes. Ambas permanecem preservadas.

## Verificação e pendências

88 testes direcionados aprovados com warnings como erros; Ruff aprovado e mypy do novo módulo aprovado. A suíte completa anterior de 574 testes não foi repetida. Não houve coleta de novos dados, fitting, calibração ou promoção.

O diagnóstico horário e o inventário local estão tecnicamente concluídos. Permanecem:

1. Revisar cientificamente os limites das fontes e da amostra e decidir a independência das reservas à luz da proveniência disponível.
2. Definir revisor, evento/métrica principal, suporte mínimo, ganho aceitável, tradeoffs, estratos críticos e tratamento das janelas curtas/multiplicidade.
3. Consolidar uma nova versão prospectiva do protocolo e o congelamento final, se as decisões anteriores permitirem.

As causas dos erros continuam não comprovadas. A etapa original 6 permanece bloqueada e a reference-v1 continua ativa. O PDF acadêmico permanece inalterado.
