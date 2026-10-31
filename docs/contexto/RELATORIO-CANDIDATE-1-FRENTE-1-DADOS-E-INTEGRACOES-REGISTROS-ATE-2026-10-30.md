# Candidate-1 — Frente 1: Dados e integrações

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Piloto técnico adaptativo — observações restauradas em 30/10/2026

O acesso oficial TEMPO pelo navegador permitiu baixar os CSVs recentes das três estações; a API direta continua 204. Conversão explícita e rastreável entregue sem alterar o importador anual. Janela recente concluída: chuva/rajada 168/168 horas válidas em A201/A001/A801. Preflight renovado 15/15; D+1 disponível nos cinco braços; prontidão técnica de chuva aprovada, sem ganho de precisão calculado.

Usuário autorizou automação diária às 15h Brasília e depois reposição até completar a cota **sem data-limite**. Automação `piloto-t-cnico-climaprev` ativa; primeira janela 31/10 18 UTC. Regra: 14 capturas D+1 elegíveis por estação/modelo, 210 no total; pares completos deixam de ser consultados. Perdas viram novas datas futuras, sem backfill nem retirada do histórico de falhas. Notebook/Codex indisponíveis podem perder slots; a cauda observacional acompanha o último D+7 real. Calendário científico condicional exige revisão se as reposições ultrapassarem desenvolvimento; nenhuma confirmação/promoção autorizada. Zero slots de piloto executados nesta preparação; diagnóstico não conta na cota.

Código de importação e planejamento/auditoria de cota testado; conferir qualificação remota do novo SHA antes de transferir a aprovação anterior de 0471a98. Estado completo e comandos: `docs/operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md`; protocolo v5: `docs/planejamento/reference-candidate-1/protocolo-piloto-adaptativo-2026-10-30.json`; evidências: `docs/planejamento/reference-candidate-1/evidence/observacoes-tempo-piloto-adaptativo-2026-10-30.json`. Este estado supera o bloqueio de observações e os calendários fixos anteriores, mantendo reference-v1 padrão e demais pendências científicas/auditivas/comerciais.


## Preparação vigente das etapas 1 a 6 — 30/10/2026

Merge cab7d8c publicado na develop, com CI 41081566586 e Security 41081566583 aprovados. Protocolo/critério/partições conciliados com o runner recebido; catálogo e contratos oficiais revisados; acesso recente INMET repetido (204 nas três estações, índice anual até setembro). Calendário desativado replanejado para 31/10–13/11, 18 UTC/15h Brasília, 210 jobs e 630 alvos até 20/11. Seleção condicional deslocada a 05/12 para preservar embargo de emissões D+7; confirmação não iniciada.

Prontidão executada: **não pronto**, por observações recentes ausentes, janela antiga e preflight de 28/10. Gate reforçado para bloquear preflight com mais de 24h, relógio ausente ou futuro. 34 testes direcionados, Ruff integral e mypy dos dois módulos aprovados; verificar CI próprio do incremento. Nenhuma campanha ativada, registros E1/E2/E3 emitidos, fitting, resultado reservado novo ou promoção. Reference-v1 permanece padrão. Critérios dependentes de suporte e bloco final seguem explicitamente condicionais. Ler `docs/operacoes/preparacao-piloto-etapas-1-a-6-2026-10-30.md` e `docs/planejamento/reference-candidate-1/protocolo-consolidado-2026-10-30.md`. Este estado supera o registro anterior de merge apenas local e os calendários antigos; preserva os demais checkpoints como histórico.


## Integração vigente da develop2 — 30/10/2026

Incorporada a origem `origin/develop2` (`9fd99b7`) à versão local, preservando o incremento da frente 2 (`bd7fbe3`). A origem acrescenta protocolo, partições, observações, campanha/cobertura, comparação/relatórios e infraestrutura de registro, seleção, confirmação técnica e adaptação explícita da candidata. Essas entregas usam ensaios sintéticos: não encerram campanha ou aprovação científica reais. Reference-v1 segue padrão; candidata não selecionada. Calendários antigos precisam de nova versão deliberada antes de execução; sem backfill. Relatório de conciliação e qualificação: `docs/operacoes/merge-develop2-frentes-2026-10-30.md`. Este checkpoint supera afirmações históricas abaixo de ausência dessa infraestrutura. Qualificação combinada: 1.099 testes backend, mypy em 93 módulos, Ruff integral; 56 testes frontend, lint e build com Node.js 22.23.2 aprovados. Merge exclusivamente local, sem push ou alteração da main.


Atualizado em 27/10/2026. Este relatório distribui responsabilidades de implementação; não autoriza início da campanha científica nem promoção da candidata.

## Handoff da Frente 2 em 28/10/2026

Parser e pareamento experimental de temperatura/umidade/rajada, comparação com cobertura planejada e prontidão observacional entregues. Fonte oficial anual de 2026 até setembro obtida para as três estações; Belém coincide com o catálogo nessa versão. Outubro e equivalência instrumental ainda pendentes; piloto desativado, preflight pontual 15/15. Ler [relatório da continuidade](../operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md). São entregas experimentais, não conclusão científica ou integração pública. Esse estado atualiza os registros de ausência de parser/pareamento adicional abaixo.

## Atualização de contratos e integração — 28/10/2026

A revisão oficial corrigiu o protótipo: o campo térmico observado é média horária, não instantâneo; umidade tem agregação não resolvida e vento observado é média de dez minutos. Não habilitar pareamento instantâneo apenas pela presença de coluna. Rajada/chuva seguem contratos específicos, sem certificação de altura/calibração por estação. O relatório offline agora integra arquivos, CSV e horizontes/cobertura e devolve bloqueios do piloto; nova fonte observacional atual permanece necessária. Ver [contratos verificados](../planejamento/reference-candidate-1/contratos-instrumentais-verificados-2026-10-28.md).

## Objetivo

Fornecer previsões e observações comparáveis, rastreáveis e com qualidade explícita para a avaliação da candidate-1. Esta frente responde pela engenharia dos dados e pela operação experimental da coleta.

## Implementações sob responsabilidade desta frente

| ID | Implementação | Estado atual | Entrega necessária para conclusão |
|---|---|---|---|
| F1-01 | Selecionar as duas fontes adicionais | Seleção final pendente; coletores experimentais de GFS, IFS e ICON pela Open-Meteo e MET Norway existentes | Registrar fontes escolhidas, modelos de origem, cobertura brasileira, campos, limites, atribuição e compatibilidade com o uso pretendido. APIs diferentes podem repetir o mesmo modelo |
| F1-02 | Concluir adaptadores e normalização das fontes selecionadas | Parcial: coleta pontual e normalização experimental implementadas | Validar contratos, unidades, instantes e intervalos; preservar ausência de dados e rejeitar valores inválidos. Integrar ao fluxo experimental, mantendo a consulta pública atual |
| F1-03 | Arquivar previsões e proveniência | Implementado no escopo experimental | Manter arquivos imutáveis, hashes, identidade de modelo/provedor, rodada quando disponível, horário de coleta, ponto, fuso e versões. Registrar limitações da baseline e de rodadas desconhecidas |
| F1-04 | Controlar orçamento, duplicação e falhas de coleta | Implementado para executores que compartilham o mesmo ledger SQLite local | Preservar cotas por provedor/dia, reserva anterior à tentativa e resultados explícitos. Preparar procedimento de recuperação de reservas sem repetir chamadas silenciosamente; não equivale a controle distribuído entre servidores |
| F1-05 | Implementar pareamento com observações INMET | Chuva diária implementada no escopo exploratório | Ampliar para temperatura, vento/rajadas e umidade conforme equivalência aprovada pela Frente 2. Confirmar metadados das estações, qualidade, intervalos e alinhamento geográfico/temporal |
| F1-06 | Completar cobertura dos dados frente ao calendário | Parcial: auditoria operacional de jobs implementada | Relacionar manifestos completos, coletas e pares por estação, variável, dia e horizonte. Expor também alvos ausentes de todos os modelos; job concluído não significa previsão ou observação elegível |
| F1-07 | Preparar coleta recorrente e acompanhamento operacional | Runner por slot existente; sem rotina recorrente instalada | Implementar acionamento, registro de execução, diagnóstico de falhas e procedimento de recuperação. Ativar somente após aceite da campanha e calendário; não retroagir slots perdidos |
| F1-08 | Disponibilizar conjuntos versionados para avaliação | Parcial: arquivo e pareamento existentes | Entregar conjuntos de desenvolvimento, validação de seleção e teste com manifestos separados, proveniência e exclusões. Preservar reservas e impedir uso acidental de dados confirmatórios no ajuste |

“Duas fontes adicionais” é a seleção pretendida; não significa que duas APIs independentes já estejam escolhidas ou integradas à previsão pública. A origem meteorológica deve ser verificada antes da seleção final.

## Código existente relacionado

- `src/climaprev/tools/experimental_collection.py`: coleta pontual de modelos.
- `src/climaprev/tools/experimental_normalization.py`: unidades e intervalos das medições.
- `src/climaprev/tools/experimental_archive.py`: arquivamento imutável e proveniência.
- `src/climaprev/tools/experimental_baseline.py`: baseline pelo adaptador e política atuais, sem representar todo o fluxo público de cache e avisos.
- `src/climaprev/tools/experimental_campaign.py`: manifesto, ledger local e execução por slot.
- `src/climaprev/tools/experimental_pairing.py`: pareamento exploratório de chuva.
- `src/climaprev/tools/experimental_coverage.py`: diagnóstico somente leitura de jobs contra os manifestos fornecidos; não detecta manifestos omitidos pelo operador.
- `src/climaprev/tools/inmet_observations.py`: leitura e qualidade das observações de estação.

## Sequência de execução

1. Fechar o catálogo das duas fontes com evidências de origem e condições de uso.
2. Receber da Frente 2 as definições de variáveis, intervalos, pontos e elegibilidade.
3. Concluir adaptadores e pareamento das variáveis pendentes, com testes controlados.
4. Ligar cobertura operacional à cobertura meteorológica e aos conjuntos versionados.
5. Preparar a rotina e o procedimento operacional, mantendo a ativação condicionada ao aceite.
6. Executar o piloto aprovado e entregar o diagnóstico de viabilidade à Frente 2.
7. Operar a coleta do calendário aprovado, preservando as partições e os dados reservados.

## Dependências e fronteira de responsabilidade

A Frente 2 define o significado científico das variáveis, as regras de elegibilidade, o desenho temporal e os critérios de aceitação. A Frente 1 implementa essas regras na coleta e no pareamento, reportando o que não for tecnicamente comparável.

Esta frente não seleciona pesos pela qualidade observada, não declara superioridade da candidata e não promove uma nova política de risco. A integração pública da candidata fica sob a Frente 2, com os contratos de dados fornecidos por esta frente.

## Critério de conclusão

Fontes selecionadas e documentadas, contratos testados, conjuntos rastreáveis e cobertura meteorológica explícita, com operação reproduzível no calendário autorizado. Falta de dados, rodada desconhecida e intervalos incompatíveis devem permanecer visíveis.

## Referências

- [Frente 2 — Ciência, precisão e integração](RELATORIO-CANDIDATE-1-FRENTE-2-CIENCIA-E-PRECISAO.md).
- [RDP geral](RELATORIO-PENDENCIAS-2026-10-20.md).
- [Fontes e coleta](../planejamento/reference-candidate-1/fontes-e-coleta-2026-10-23.md).
- [Revisão de parâmetros ainda não aprovados](../planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md).
- [Consolidação técnica](../operacoes/consolidacao-2026-10-27.md).
