# STATE — Clima Prev

**Atualização:** 2026-09-13. [Índice](PROJECT.md).

## Estado observado

Backend de consulta meteorológica implementado em FastAPI, com Open-Meteo,
Redis, avaliação heurística, logs e testes no repositório. Esta revisão
entrega documentação; não altera código de aplicação, testes ou implantação.

| Capacidade                                          | Estado                                                           |
| --------------------------------------------------- | ---------------------------------------------------------------- |
| Consulta por texto/coordenadas e até sete dias      | Implementada.                                                    |
| Política `reference-v1` e conversão de temperaturas | Implementadas.                                                   |
| Cache, lock distribuído e rate limit                | Implementados, com limites descritos nos documentos.             |
| Health e métricas                                   | Health implementado; métricas em memória, sem exporter entregue. |
| Alertas oficiais                                    | Porta existente; provider instalado retorna `not_configured`.    |
| Frontend, autenticação, histórico, notificações     | Ausentes nesta base.                                             |
| Produção                                            | Topologia, controles e capacidade não verificados nesta revisão. |

## Decisões desta revisão

1. Usar `.md`, conforme confirmação do solicitante.
2. Aproveitar o padrão documental SIGFAS de visão, desenho, contrato,
   restrições, roadmap e estado; adaptar todo o conteúdo ao Clima Prev.
3. Manter evidência de implementação separada de propostas e resultados históricos.
4. Usar a raiz do projeto e `docs/`; não criar documentação em `specs/` ou
   `.specs/`, diretórios excluídos pelo [gitignore](.gitignore).
5. Preservar o [handoff histórico](handoff.md) como registro anterior.

## Pendências principais

- Fuso por coordenadas pode divergir do fuso dos dados solicitados ao provedor.
- Stale não tem idade revalidada ao final de esperas e retries.
- 4xx do provedor e perda de lock têm tratamento genérico 500.
- Dados faltantes não geram estado de risco indeterminado.
- Configuração, logs de acesso, imagem e Redis exigem decisões para produção.

Detalhamento: [restrições](docs/restricoes.md), [segurança](docs/seguranca.md)
e [roadmap](ROADMAP.md).

## Evidências e continuidade

O handoff de 2026-08-29 relata 148 testes aprovados e baseline de carga com
mock. Os artefatos externos citados nele não estão presentes neste checkout.
Esses números são históricos, não testes executados em 2026-09-13.

A verificação desta entrega está descrita em
[validação documental](docs/validacao-documentacao.md). Para retomar, ler
PROJECT, restrições e roadmap; selecionar a etapa e registrar seu contrato
antes de alterar comportamento. Não há commit, push ou publicação nesta entrega.

## Retomada — branch e planejamento de evolução

**Data:** 2026-09-13. **Branch ativa:** `docs/plano-evolucao-climaprev`.
**Base:** `main`, commit `a010c3b`. Branch criada no repositório existente,
preservando documentos e outras alterações locais. Não houve commit ou push.

Entregues [context](docs/planejamento/evolucao-climaprev/context.md),
[spec](docs/planejamento/evolucao-climaprev/spec.md),
[design](docs/planejamento/evolucao-climaprev/design.md) e
[tasks](docs/planejamento/evolucao-climaprev/tasks.md).
São 23 requisitos mapeados a 25 tarefas, todas pendentes de implementação.

O planejamento cobre confiabilidade, segurança, homologação local e interface
de consulta. Frontend nativo na mesma origem, contrato aditivo de qualidade,
consulta anônima e retenção operacional são premissas propostas, não decisões
de produto confirmadas. Alertas oficiais, contas e notificações permanecem
como backlog condicionado.

O pedido atual é de elaboração dos documentos. Não houve mudança em código
de aplicação, testes ou configuração de execução nesta etapa.
`validate_spec.py --strict` e `validate_tasks.py --strict` passaram com zero
erros e zero avisos. Isso valida o planejamento, não os requisitos executáveis.
O próximo passo técnico do plano é T1, após revisão das premissas aplicáveis.

## Handoff

- Execução solicitada em 2026-09-13: 25 tarefas, branch `atualizaçao-geral`.
- Blocos de agentes: T1–T10, T11–T20, T21–T25; revisão independente ao final.
- Documentação de origem preservada em commit de preparação.
- Alterações preexistentes em `docker-compose.yml`, `.harness-eval/` e
  `.notebook/` preservadas; não incluí-las por engano nos commits das tarefas.
- Docker local usa backend Podman; acesso disponível com permissão de ferramenta.
- Próximo passo: baseline e T1. Nenhuma tarefa concluída até esta preparação.
