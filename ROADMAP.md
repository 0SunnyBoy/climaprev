# ROADMAP — Clima Prev

**Data:** 2026-09-13. **Estado:** evolução proposta a partir da análise local.
As prioridades abaixo não indicam implementação iniciada ou cronograma
aprovado. [Índice](PROJECT.md).

| Etapa                          | Objetivo                                                                                                    | Entrega / critério de conclusão                                                                                      |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| R0 — Documentação              | Consolidar arquitetura e contratos.                                                                         | Documentos por tema com links válidos, estados explícitos e limitações registradas. Entregue nesta revisão.          |
| R1 — Consistência dos dados    | Resolver fuso por coordenadas, cobertura horária, dados não finitos e sinalização de incompletude.          | Contratos definidos e testes com fuso local, valores ausentes e séries inconsistentes.                               |
| R2 — Falhas e configuração     | Revalidar stale antes da resposta, mapear 4xx do provedor e perda de lock, validar números da configuração. | Casos de erro previsíveis e testes de fronteira de TTL, indisponibilidade e configuração inválida.                   |
| R3 — Preparação de implantação | Definir entrada HTTPS, Redis, logs, cotas, imagem e métricas.                                               | Evidência dos controles descritos em segurança, isolamento do perfil de carga e métricas coletadas fora do processo. |
| R4 — Frontend                  | Criar consulta e visualização usando a API.                                                                 | Jornada com loading, erro, stale, null, fonte, aviso e alertas não configurados; sem recalcular risco.               |
| R5 — Alertas oficiais          | Implementar fonte e cobertura explicitamente definidas.                                                     | Adaptador real, testes de contrato e estados available/unavailable, sem misturar com risco heurístico.               |
| R6 — Personalização            | Avaliar contas, favoritos, histórico e notificações.                                                        | Escopo próprio com autorização, dados, retenção e contratos definidos antes da implementação.                        |

## Decisões pendentes

| ID     | Decisão                                                           | Quando resolver                               |
| ------ | ----------------------------------------------------------------- | --------------------------------------------- |
| DEC-01 | Consulta pública anônima ou consumidores autenticados?            | Antes de exposição ampla ou dados privados.   |
| DEC-02 | Horizonte de datas permitido e tratamento de datas indisponíveis? | R1/R2, antes de fechar validação do frontend. |
| DEC-03 | Como expor incompletude e eventual risco indeterminado?           | R1; o contrato hoje só tem low/moderate/high. |
| DEC-04 | Qual infraestrutura e orçamento de chamadas externas?             | R3.                                           |
| DEC-05 | Qual destino/retenção dos logs e tratamento de localização/IP?    | R3.                                           |
| DEC-06 | Qual fonte de alertas e abrangência geográfica?                   | R5.                                           |
| DEC-07 | Como validar a política de risco para o público-alvo?             | Antes de ampliar as afirmações do produto.    |

Não copiar a estrutura operacional do SIGFAS como dependência do produto.
A próxima etapa técnica recomendada é R1/R2: fechar a semântica dos dados e
erros antes de desenvolver a apresentação e publicar o serviço.

## Desdobramento em tarefas

O [plano de evolução](docs/planejamento/evolucao-climaprev/context.md)
transforma este roadmap em quatro documentos de planejamento. O
[tasks.md](docs/planejamento/evolucao-climaprev/tasks.md) detalha:

| Roadmap                   | Tarefas planejadas                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| R1 — Dados                | T1–T5: fuso, validação, completude, média e identidade do cache.                         |
| R2 — Resiliência          | T6–T11: expiração, corrupção, falhas, lock e configuração.                               |
| R3 — Segurança e operação | T12–T20: proxies, logs, cotas, métricas, imagem e homologação local.                     |
| R4 — Interface            | T21–T25: formulário, API, resultado, estados e acessibilidade.                           |
| R5/R6 — Expansão          | Backlog condicionado; ainda depende de fonte de alertas e contratos de identidade/dados. |

As decisões técnicas do plano estão registradas como premissas revisáveis.
Esta atualização não indica implementação, homologação ou publicação.
