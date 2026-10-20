# PROJECT — Clima Prev

**Publicação e qualificação em 20/10/2026:** atualização enviada à develop; lote funcional `f0eab5e` aprovado em CI e Security gates. As correções de imagem/CSP passaram remotamente. Não houve merge em main ou deploy. Estado e pendências vigentes no [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md); descrições de alterações não enviadas/CI pendente abaixo pertencem aos lotes anteriores.

**Atualização vigente (20/10/2026):** backend e frontend 0.1.0 em desenvolvimento; develop, base 23bf4ce, alterações locais sem commit/push. Desacoplamento, datas/fusos, avisos, prazo, interface, CI local, métricas e carga revisados. 644 testes backend e 27 frontend aprovados. [STATE](STATE.md) e [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) são as fontes do estado vigente. Prioridades: INMET real, CI remota, revisão científica preparatória, critérios de aprovação e acessibilidade manual. Evolução da candidate-1 por último, focada em qualidade/precisão; reference-v1 preservada. Hospedagem adiada; horizonte de 14 dias só planejado. A análise datada abaixo é histórica.

**Revisão vigente:** 20/10/2026; análise original de 25/09 preservada nas referências históricas.
**Estado:** rework Vue, avaliação diária de risco, prioridade de alertas oficiais
e contrato do maior risco implementados; o pipeline offline de validação histórica
está disponível, mas a aprovação científica e a calibração permanecem pendentes.

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

Estado consolidado: [STATE](STATE.md). Pendências atuais: [RDP 20/10](../../RELATORIO-PENDENCIAS-2026-10-20.md). Cobertura da revisão: [sincronização documental](SINCRONIZACAO-DOCUMENTAL-2026-10-20.md).


| Arquivo                                                          | Conteúdo                                                    |
| ---------------------------------------------------------------- | ----------------------------------------------------------- |
| [Arquitetura](../arquitetura/arquitetura.md)                               | Componentes, camadas, dependências e implantação.           |
| [Fluxos](../arquitetura/fluxos.md)                                         | Consulta, cache, concorrência, falhas e jornada web.     |
| [Fluxos de informação](../arquitetura/fluxos-informacao.md)                | Dados enviados, recebidos, transformados e armazenados.     |
| [Parâmetros de predição](../arquitetura/parametros-de-predicao.md)                   | Entradas, variáveis meteorológicas e limiares do risco.     |
| [Validação e calibração](../arquitetura/validacao-e-calibracao.md)          | Protocolo histórico, pico diário e fallback estatístico.    |
| [Continuação e escopo de previsão](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md) | Validação offline, fallback e critérios de ampliação. |
| [Segurança](../seguranca/seguranca.md)                                   | Fronteiras de confiança, controles existentes e lacunas.    |
| [Restrições](../operacoes/restricoes.md)                                 | Regras de entrada, limites operacionais e de interpretação. |
| [Análise dos modelos SIGFAS](../arquitetura/analise-referencias-sigfas.md) | Estrutura aproveitada e diferenças entre projetos.          |
| [Análise documental inicial](../operacoes/validacao-documentacao.md)                      | Evidências, rastreabilidade e limites da verificação.       |
| [ROADMAP](ROADMAP.md)                                            | Escopo de evolução e critérios de conclusão.               |
| [STATE](STATE.md)                                                | Estado observado, decisões e pendências.                    |
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
