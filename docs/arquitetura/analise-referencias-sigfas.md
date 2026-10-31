# Análise das referências do SIGFAS

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Data:** 2026-09-13. **Método:** leitura de documentos locais e comparação
com a implementação do Clima Prev. [Índice](../projeto/PROJECT.md).

## Referências examinadas

Os modelos encontrados em `/home/ney/Documentos/fullstack` usam `.md`.
Nenhum arquivo `.mb` foi localizado nesse diretório durante o levantamento.
A extensão `.md` foi confirmada pelo solicitante.

| Referência no fullstack                              | Estrutura aproveitada                                                |
| ---------------------------------------------------- | -------------------------------------------------------------------- |
| `PROJECT.md`                                         | Visão sistêmica, mapa do workspace, componentes e fontes de verdade. |
| `ROADMAP.md` e `STATE.md`                            | Separação entre evolução futura, estado atual e histórico.           |
| `specs/context.md`                                   | Tabelas de fatos, evidências e consequências para integração.        |
| `specs/spec.md`                                      | Escopo, casos de uso, restrições e rastreabilidade.                  |
| `specs/design.md`                                    | Responsabilidades, fluxo, contrato HTTP e estados de erro.           |
| `.spec/features/cadastro-cobranca-dominio/design.md` | Distinção entre desenho proposto e comportamento observado.          |
| `.spec/analysis/sigfas-docs-vs-realidade/spec.md`    | Registro explícito de divergências entre documentação e código.      |

Esses caminhos são referências de origem, não dependências necessárias para
usar os novos documentos do Clima Prev. Não foi feita uma nova auditoria do
código SIGFAS nem confirmada a situação atual das features descritas ali.

## O que adaptar

| Tema        | Referência SIGFAS                          | Aplicação no Clima Prev                                                       |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| Arquitetura | Portal e monólito com vários domínios.     | API com camadas e adaptadores; frontend futuro separado.                      |
| Informação  | Contratos por operação e responsabilidade. | Query HTTP, previsão normalizada, risco e metadados.                          |
| Segurança   | Fronteiras de autorização explícitas.      | API hoje sem login; CORS, identificação por IP e controles de infraestrutura. |
| Fluxo       | Estados e tratamento de erro.              | Consulta, cache, indisponibilidade e informação incompleta.                   |
| Restrições  | Limites funcionais e pré-condições.        | Sete dias, exclusividade de localização, TTL e uso da estimativa.             |
| Evidências  | Rastreabilidade para arquivos reais.       | Links para código e testes presentes neste checkout.                          |

Não transportar Keycloak, PostgreSQL, tenant, roles militares, financeiro,
cadastro de associados ou regras de estoque para o Clima Prev: esses elementos
pertencem ao domínio do SIGFAS e não estão implementados aqui.

## Ajustes necessários em relação ao histórico do Clima Prev

O [handoff](../projeto/handoff.md) registra resultados de 2026-08-29, um caminho Windows
e referências a `.specs/`, `.superpowers/` e `docs/superpowers/`. Essas pastas
não estão presentes neste checkout. Os resultados históricos não são
reclassificados como validação atual, e os caminhos ausentes não são usados
como links de navegação.

O mesmo cuidado vale para capacidades: uma porta para alertas oficiais não
significa uma integração ativa; contadores em memória não significam um
exportador de métricas instalado; um namespace Redis por ambiente não significa
isolamento de usuários ou organizações.
