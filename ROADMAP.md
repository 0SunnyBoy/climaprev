# ROADMAP — Clima Prev

**Data:** 2026-09-13. **Estado:** execução local autorizada.
O progresso e as evidências por tarefa estão no plano de evolução; este
roadmap mantém a divisão de escopo. [Índice](PROJECT.md).

| Etapa                          | Objetivo                                                                                                    | Entrega / critério de conclusão                                                                                      |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| R0 — Documentação              | Consolidar arquitetura e contratos.                                                                         | Documentos por tema com links válidos, estados explícitos e limitações registradas. Entregue nesta revisão.          |
| R1 — Consistência dos dados    | Resolver fuso por coordenadas, cobertura horária, dados não finitos e sinalização de incompletude.          | Contratos definidos e testes com fuso local, valores ausentes e séries inconsistentes.                               |
| R2 — Falhas e configuração     | Revalidar stale antes da resposta, mapear 4xx do provedor e perda de lock, validar números da configuração. | Casos de erro previsíveis e testes de fronteira de TTL, indisponibilidade e configuração inválida.                   |
| R3 — Preparação de implantação | Definir entrada HTTPS, Redis, logs, cotas, imagem e métricas.                                               | Evidência dos controles descritos em segurança, isolamento do perfil de carga e snapshot interno identificado por processo. |
| R4 — Frontend                  | Criar consulta e visualização usando a API.                                                                 | Jornada com loading, erro, stale, null, fonte, aviso e alertas não configurados; sem recalcular risco.               |
| R5 — Alertas oficiais          | Implementar fonte e cobertura explicitamente definidas.                                                     | Adaptador real, testes de contrato e estados available/unavailable, sem misturar com risco heurístico.               |
| R6 — Personalização            | Avaliar contas, favoritos, histórico e notificações.                                                        | Escopo próprio com autorização, dados, retenção e contratos definidos antes da implementação.                        |

R0–R4 foram implementadas no ciclo de 25 tarefas. A revisão independente
final está pendente; consulte STATE e as evidências por tarefa. R5/R6
continuam fora do escopo entregue.

## Decisões e limites do ciclo

| ID     | Decisão                                                                                      | Quando resolver                                           |
| ------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| DEC-01 | Consulta anônima neste ciclo; operações pessoais ficam fora.                                 | Rever antes de dados privados.                            |
| DEC-02 | Até sete dias, sem horizonte adicional fixo; indisponibilidade vira erro externo sanitizado. | Contrato preservado.                                      |
| DEC-03 | Completude aditiva complete/partial/unavailable, com os níveis de risco existentes.          | Implementado em T3; apresentação em T23.                  |
| DEC-04 | Homologação local isolada e cota externa configurável.                                       | Orçamento real e infraestrutura pública seguem pendentes. |
| DEC-05 | Logs sanitizados com retenção local de sete dias.                                            | Entrega/verificação em T13/T20.                           |
| DEC-06 | Qual fonte de alertas e abrangência geográfica?                                              | R5.                                                       |
| DEC-07 | Como validar a política de risco para o público-alvo?                                        | Antes de ampliar as afirmações do produto.                |

A estrutura documental do SIGFAS é uma referência, sem dependência entre
os produtos. R1/R2 são integradas antes de R3/R4. Publicação externa não faz
parte deste ciclo; a homologação deste ciclo é local.

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

As decisões técnicas do plano estão registradas como premissas adotadas na
execução local. Alertas oficiais e personalização continuam condicionados a
contratos próprios; os resultados executados ficam no STATE e nas evidências.
