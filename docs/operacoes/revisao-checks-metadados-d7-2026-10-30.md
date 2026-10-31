# Checks publicados, metadados e controle D+7 — 30/10/2026

> **Continuação concluída:** [refatoração e infraestrutura D+7](refatoracao-controle-d7-2026-10-30.md) implementadas posteriormente. Este relatório preserva a etapa de desenho anterior e os checks do commit `355a158`.

## Qualificação remota

Commit publicado conferido: `355a158ce91792b3bb8cb777219049b92f833839`, branch develop.

| Workflow | Resultado | Execução |
|---|---|---|
| CI | Concluído, sucesso | [41152086801](https://github.com/0SunnyBoy/climaprev/actions/runs/41152086801) |
| Security gates | Concluído, sucesso | [41152086839](https://github.com/0SunnyBoy/climaprev/actions/runs/41152086839) |

Verificação em 31/10 UTC, noite local de 30/10. A aprovação pertence a esse SHA; novos documentos desta rodada são alterações locais posteriores e não herdam qualificação remota própria.

## Entregas

- [Revisão instrumental](../planejamento/reference-candidate-1/metadados-instrumentais-2026-10-30.md) e inventário estruturado por estação, com contratos temporais e lacunas explícitas.
- [Desenho prospectivo D+7](../planejamento/reference-candidate-1/controle-d7-prospectivo-2026-10-30.md) e plano estruturado desativado. Especifica alvo, identidade, arquivos, cobertura, orçamento, partições, falhas e testes para uma futura implementação separada.
- [Evidência de preparação](../planejamento/reference-candidate-1/evidence/metadados-controle-d7-2026-10-30.json), sem previsão nova, ajuste, promoção ou alteração da automação.

## Verificações e limitações

Quatro testes existentes de revisão instrumental aprovados. Hashes dos três registros do catálogo conferem com a proveniência dos CSVs; calendário v5 ativo validado contra o código atual. Ledger e calendário não foram alterados. Três exemplos de D+7 validados: 31/10 18 UTC → 07/11 local, 03 UTC a 03 UTC do dia seguinte, antecedência de 153 horas até o início do alvo.

Catálogo e documentação oficial acessíveis pelo mecanismo web; nova obtenção bruta do catálogo pelo terminal falhou. O inventário usa explicitamente o snapshot oficial anterior, sem declarar nova captura. Altura, calibração e representatividade individuais não foram comprovadas e continuam lacunas. Temperatura média versus instantânea, vento médio versus instantâneo e umidade ambígua permanecem bloqueados.

O **desenho** do controle D+7 está concluído; o **coletor** não está implementado ou ativado. Nova campanha exige versões, calendário, partições e registro de execução próprios. Não modifica a cota de 210, não preenche retrospectivamente a baseline do piloto e não sustenta superioridade da candidate-1.

## Próximos passos

Obter fichas instrumentais oficiais por estação/período; implementar o controle sucessor em escopo separado; qualificar cobertura D+7 e orçamento total antes de ativação. Enquanto isso, manter o piloto autorizado e a reference-v1 padrão. [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).
