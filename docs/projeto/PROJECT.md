# PROJECT — Clima Prev

**Data da análise:** 2026-09-24.
**Estado:** P0–P2.6 e rework Vue concluídos; estado atual publicado em
`develop`; revisão independente final pendente.

## Visão

O Clima Prev consulta previsões meteorológicas de curto prazo e calcula uma
estimativa de risco para um local e um período de até sete dias. A resposta
informa a fonte, a qualidade dos dados, a política usada e a disponibilidade
de alertas oficiais. A estimativa não substitui alertas das autoridades.

O sistema reúne uma interface web Vue/TypeScript compilada pelo Vite e servida pelo Nginx, backend
Python/FastAPI, Redis, adaptadores Open-Meteo e integração de avisos ativos do
INMET. Contas de usuário, notificações e personalização continuam fora deste
ciclo.

## Documentação do projeto

| Arquivo                                                          | Conteúdo                                                    |
| ---------------------------------------------------------------- | ----------------------------------------------------------- |
| [Arquitetura](../arquitetura/arquitetura.md)                               | Componentes, camadas, dependências e implantação.           |
| [Fluxos](../arquitetura/fluxos.md)                                         | Consulta, cache, concorrência, falhas e jornada web.     |
| [Fluxos de informação](../arquitetura/fluxos-informacao.md)                | Dados enviados, recebidos, transformados e armazenados.     |
| [Parâmetros de predição](../arquitetura/parametros-de-predicao.md)                   | Entradas, variáveis meteorológicas e limiares do risco.     |
| [Continuação e escopo de previsão](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md) | Validação offline, fallback e critérios de ampliação. |
| [Segurança](../seguranca/seguranca.md)                                   | Fronteiras de confiança, controles existentes e lacunas.    |
| [Restrições](../operacoes/restricoes.md)                                 | Regras de entrada, limites operacionais e de interpretação. |
| [Análise dos modelos SIGFAS](../arquitetura/analise-referencias-sigfas.md) | Estrutura aproveitada e diferenças entre projetos.          |
| [Análise documental inicial](../operacoes/validacao-documentacao.md)                      | Evidências, rastreabilidade e limites da verificação.       |
| [ROADMAP](ROADMAP.md)                                            | Escopo de evolução e critérios de conclusão.               |
| [STATE](STATE.md)                                                | Estado observado, decisões e pendências.                    |
| [Contexto de retomada](context.md)                              | Branch ativa, validações recentes e como continuar.         |
| [Visão geral](overview.md)                                       | Arquitetura, tecnologias, operação e limites do projeto.    |
| [Operações](../operacoes/operations.md)                                  | Comandos e configuração já documentados.                    |
| [CI](../../.github/workflows/ci.yml)                            | Validação automática no GitHub.                             |

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
| `frontend/`                      | Código-fonte Vue/TypeScript, build Vite e apresentação do contrato público. |
| `docker/frontend/nginx.conf`    | Nginx local para servir o frontend e encaminhar API/health. |
| `docker/homolog/entrada/nginx.conf` | Nginx TLS de homologação para servir o frontend e encaminhar API/health. |
| `src/climaprev/api/`            | Contrato HTTP, validação, rate limit e observabilidade. |
| `src/climaprev/application/`    | Orquestração de consulta e portas de integração.        |
| `src/climaprev/domain/`         | Modelos, unidades e política de risco.                  |
| `src/climaprev/infrastructure/` | Clientes HTTP, Redis, Open-Meteo e INMET.             |
| `src/climaprev/api/routes/locations.py` | Busca de localidades e sugestões.                 |
| `src/climaprev/main.py`         | Composição de dependências e ciclo de vida.             |
| `tests/`                        | Testes unitários, integração, contrato, Docker e carga. |
| `docker-compose.yml`            | Execução local e perfil separado de carga.              |

## Escopo da documentação

Este ciclo documenta e implementa a evolução da arquitetura, da integração
e da interface do Clima Prev. A estrutura foi adaptada dos documentos do SIGFAS; não existe
integração de dados entre os dois sistemas identificada neste projeto.

Os diagramas Mermaid são editáveis como texto nos próprios arquivos `.md`.

## Planejamento de implementação

O [contexto da evolução](../planejamento/evolucao-climaprev/context.md)
consolida as premissas do ciclo em execução. A
[spec](../planejamento/evolucao-climaprev/spec.md) contém 23 requisitos,
o [design](../planejamento/evolucao-climaprev/design.md) define os contratos
adotados e as [tasks](../planejamento/evolucao-climaprev/tasks.md)
organizam 25 tarefas em cinco fases. Os incrementos P0–P2.6 estão registrados
no [estado atual](STATE.md) e no [catálogo de implementações](ImplementationsAndRefactoring.md).
Consulte
[STATE](STATE.md) para o checkpoint e as tarefas para o progresso por requisito.
