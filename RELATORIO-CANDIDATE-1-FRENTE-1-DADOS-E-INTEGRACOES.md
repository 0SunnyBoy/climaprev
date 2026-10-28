# Candidate-1 — Frente 1: Dados e integrações

Atualizado em 27/10/2026. Este relatório distribui responsabilidades de implementação; não autoriza início da campanha científica nem promoção da candidata.

## Handoff da Frente 2 em 28/10/2026

Parser e pareamento experimental de temperatura/umidade/rajada, comparação com cobertura planejada e prontidão observacional entregues. Fonte oficial anual de 2026 até setembro obtida para as três estações; Belém coincide com o catálogo nessa versão. Outubro e equivalência instrumental ainda pendentes; piloto desativado, preflight pontual 15/15. Ler [relatório da continuidade](docs/operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md). São entregas experimentais, não conclusão científica ou integração pública. Esse estado atualiza os registros de ausência de parser/pareamento adicional abaixo.

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
- [Fontes e coleta](docs/planejamento/reference-candidate-1/fontes-e-coleta-2026-10-23.md).
- [Revisão de parâmetros ainda não aprovados](docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md).
- [Consolidação técnica](docs/operacoes/consolidacao-2026-10-27.md).
