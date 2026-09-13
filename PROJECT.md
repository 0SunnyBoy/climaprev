# PROJECT — Clima Prev

**Data da análise:** 2026-09-13.  
**Estado:** implementação local entregue pelos agentes na branch
`atualizaçao-geral`; fechamento e revisão independente em andamento.

## Visão

O Clima Prev consulta previsões meteorológicas de curto prazo e calcula uma
estimativa de risco para um local e um período de até sete dias. A resposta
informa a fonte, a qualidade dos dados, a política usada e a disponibilidade
de alertas oficiais. A estimativa não substitui alertas das autoridades.

O sistema reúne uma interface web na mesma origem, backend Python/FastAPI,
Redis e adaptadores Open-Meteo. Contas de usuário, notificações e integração real de alertas oficiais ficam
fora deste ciclo.

## Documentação do projeto

| Arquivo                                                          | Conteúdo                                                    |
| ---------------------------------------------------------------- | ----------------------------------------------------------- |
| [Arquitetura](docs/arquitetura.md)                               | Componentes, camadas, dependências e implantação.           |
| [Fluxos](docs/fluxos.md)                                         | Consulta, cache, concorrência, falhas e jornada web.     |
| [Fluxos de informação](docs/fluxos-informacao.md)                | Dados enviados, recebidos, transformados e armazenados.     |
| [Segurança](docs/seguranca.md)                                   | Fronteiras de confiança, controles existentes e lacunas.    |
| [Restrições](docs/restricoes.md)                                 | Regras de entrada, limites operacionais e de interpretação. |
| [Análise dos modelos SIGFAS](docs/analise-referencias-sigfas.md) | Estrutura aproveitada e diferenças entre projetos.          |
| [Análise documental inicial](docs/validacao-documentacao.md)                      | Evidências, rastreabilidade e limites da verificação.       |
| [ROADMAP](ROADMAP.md)                                            | Escopo de evolução e critérios de conclusão.               |
| [STATE](STATE.md)                                                | Estado observado, decisões e pendências.                    |
| [Operações](docs/operations.md)                                  | Comandos e configuração já documentados.                    |

## Como interpretar os documentos

- **Implementado:** comportamento encontrado nos arquivos de código citados.
- **Proposto:** desenho ou requisito para uma próxima implementação.
- **Pendente:** decisão ou verificação ainda necessária.
- **Histórico:** resultado relatado anteriormente, sem nova execução aqui.

Esses estados não representam homologação em produção. O código atual é a
referência para comportamento existente; propostas descrevem mudanças futuras.

## Mapa do workspace

| Local                           | Papel                                                   |
| ------------------------------- | ------------------------------------------------------- |
| `src/climaprev/web/` | Interface de consulta e apresentação do contrato público. |
| `src/climaprev/api/`            | Contrato HTTP, validação, rate limit e observabilidade. |
| `src/climaprev/application/`    | Orquestração de consulta e portas de integração.        |
| `src/climaprev/domain/`         | Modelos, unidades e política de risco.                  |
| `src/climaprev/infrastructure/` | Clientes HTTP e adaptadores Redis/Open-Meteo.           |
| `src/climaprev/main.py`         | Composição de dependências e ciclo de vida.             |
| `tests/`                        | Testes unitários, integração, contrato, Docker e carga. |
| `docker-compose.yml`            | Execução local e perfil separado de carga.              |

## Escopo da documentação

Este ciclo documenta e implementa a evolução da arquitetura, da integração
e da interface do Clima Prev. A estrutura foi adaptada dos documentos do SIGFAS; não existe
integração de dados entre os dois sistemas identificada neste projeto.

Os diagramas Mermaid são editáveis como texto nos próprios arquivos `.md`.

## Planejamento de implementação

O [contexto da evolução](docs/planejamento/evolucao-climaprev/context.md)
consolida as premissas do ciclo em execução. A
[spec](docs/planejamento/evolucao-climaprev/spec.md) contém 23 requisitos,
o [design](docs/planejamento/evolucao-climaprev/design.md) define os contratos
adotados e as [tasks](docs/planejamento/evolucao-climaprev/tasks.md)
organizam 25 tarefas em cinco fases. A execução ocorre na branch
`atualizaçao-geral`, com agentes, testes e commits locais. Consulte
[STATE](STATE.md) para o checkpoint e as tarefas para o progresso por requisito.
