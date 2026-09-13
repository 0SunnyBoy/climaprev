# Contexto — evolução do Clima Prev

**Data:** 2026-09-13. **Estado:** execução local autorizada, em andamento.
**Branch:** `atualizaçao-geral`. O planejamento começou em
`docs/plano-evolucao-climaprev`, a partir de `main`, commit `a010c3b`.
As alterações locais anteriores foram preservadas.

## Objetivo solicitado

Criar uma branch no Clima Prev e transformar a documentação de arquitetura,
fluxos, informação, segurança e restrições em especificação, design e tarefas
para evolução do sistema. A extensão confirmada pelo usuário é `.md`.

| Artefato               | Uso                                                      |
| ---------------------- | -------------------------------------------------------- |
| [spec.md](spec.md)     | Comportamentos esperados e critérios de aceite.          |
| [design.md](design.md) | Componentes, contratos e decisões técnicas propostas.    |
| [tasks.md](tasks.md)   | Ordem de implementação, testes e critérios de conclusão. |

## Fontes de entrada

| Documento                                 | Como orienta este plano                                 |
| ----------------------------------------- | ------------------------------------------------------- |
| [PROJECT](../../../PROJECT.md)            | Limites do produto e mapa do código.                    |
| [Arquitetura](../../arquitetura.md)       | Reutilizar API, aplicação, domínio e adaptadores.       |
| [Fluxos](../../fluxos.md)                 | Atualização concorrente, stale e erros.                 |
| [Informações](../../fluxos-informacao.md) | Contrato HTTP e dados que cruzam fronteiras.            |
| [Segurança](../../seguranca.md)           | Controles existentes e pendências PEN-01 a PEN-09.      |
| [Restrições](../../restricoes.md)         | Qualidade, fuso, limites e interpretação da estimativa. |
| [ROADMAP](../../../ROADMAP.md)            | R1/R2 como base, R3 de preparação e R4 de interface.    |
| [STATE](../../../STATE.md)                | Separar histórico de resultados atuais.                 |

## Base inicial confirmada no repositório

- Python 3.12, FastAPI, HTTPX e Redis; testes pytest, respx, Ruff e mypy.
- `GET /api/v1/risk`, consulta anônima, período máximo de sete dias.
- `reference-v1`, cálculo em Celsius e conversão apenas na saída.
- Redis para cache, lock e limite por IP; rotas de saúde existentes.
- Não há frontend nem fonte real de alertas oficiais.
- Documentos anteriores e formatação de `docker-compose.yml` já estavam no
  diretório de trabalho; não foram descartados ao criar a branch.

## Fronteira do planejamento

Detalhar a evolução local do backend e uma interface pública de consulta.
Preparar o pacote técnico de implantação sem escolher um fornecedor cloud ou
publicar um ambiente. Contas, notificações e alertas oficiais permanecem no
backlog condicionado a contratos e decisões próprias.

O pedido inicial de documentação foi ampliado para implementação local e
coordenação de agentes. O progresso real e os gates estão em [tasks.md](tasks.md).

## Decisões confirmadas e premissas

**Confirmado pelo usuário:** branch no próprio projeto; usar os documentos
anteriores; entregar contexto, spec, design e tasks em Markdown; executar
as tarefas com agentes na branch `atualizaçao-geral`.

**Premissas escolhidas para tornar o plano concreto, ainda revisáveis:**

| Tema                     | Escolha usada neste plano                                                           | Motivo                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Prioridade               | Corrigir confiabilidade antes de criar a interface.                                 | A interface depende da semântica dos dados e erros.                          |
| Compatibilidade          | Manter `/api/v1/risk` e seus campos; adicionar qualidade.                           | Evitar alteração desnecessária de consumidores.                              |
| Risco incompleto         | Acrescentar `data_quality.completeness`; manter enum de risco atual.                | Distinguir avaliação parcial sem inventar validade científica.               |
| Frontend inicial         | HTML, CSS e JavaScript nativos, servidos pela mesma aplicação.                      | Primeiro fluxo pequeno, sem novo framework ou runtime de build.              |
| Identidade               | Consulta anônima; sem persistência pessoal no navegador.                            | Não há requisito confirmado de dados privados.                               |
| Datas                    | Manter limite de sete dias sem impor horizonte adicional de calendário.             | Não transformar política mutável do provedor em regra inventada.             |
| Segurança de implantação | Perfil local de homologação com entrada TLS e Redis protegido.                      | Testar o desenho sem contratar/publicar infraestrutura.                      |
| Dados operacionais       | Não guardar query/IP em logs; retenção proposta de sete dias para logs sanitizados. | Minimizar exposição; duração é escolha de planejamento, não obrigação legal. |

As premissas acima integram o plano cuja execução foi solicitada. Revisá-las
tecnicamente antes do respectivo bloco e registrar desvios necessários,
preservando o escopo do sistema e os critérios de aceite.

## Dimensões cobertas

| Dimensão                 | Tratamento no plano                                   |
| ------------------------ | ----------------------------------------------------- |
| Validação                | CFG-01, CFG-02, DAT-01, DAT-02, CON-01.               |
| Falhas e falhas parciais | DAT-03, RES-01 a RES-04, UI-03.                       |
| Retry e duplicidade      | RES-03; GET não cria registros pessoais.              |
| Acesso e limites         | SEC-01, SEC-04; consulta anônima e métricas internas. |
| Concorrência             | CON-01, RES-01, RES-04, SEC-04.                       |
| Ciclo de vida            | RES-01, RES-02, SEC-02.                               |
| Observabilidade          | OBS-01, OBS-02, SEC-02.                               |
| Dependência externa      | RES-03, CFG-02 e provider-mock nos testes.            |
| Transições               | UI-03 e leitura fresh/stale/expired em RES-01.        |
| Pagamentos               | N/A: o produto não inclui cobrança neste escopo.      |

## Etapas futuras condicionadas

- **Alertas oficiais:** selecionar fonte, confirmar cobertura, contrato,
  atualização, expiração e tratamento de indisponibilidade. Manter
  `not_configured` até a integração estar pronta.
- **Contas/favoritos/histórico:** definir público, autenticação, autorização,
  dados, retenção e exclusão antes de introduzir persistência pessoal.
- **Notificações:** definir canais, adesão/cancelamento, destinatários,
  deduplicação e limites de envio após identidade e eventos serem definidos.
- **Política de risco:** revisão por especialista e validação regional antes
  de alterar limiares ou fazer afirmações de capacidade preditiva.

Esses itens não se tornam implementação autorizada por estarem no backlog.
Também não há seleção de provedor cloud, envio de mensagens ou publicação
incluídos nas tarefas abaixo.

## Execução autorizada em 2026-09-13

O usuário solicitou a criação da branch “atualizaçao geral” e a coordenação
de agentes para finalizar as tarefas. A branch ativa é `atualizaçao-geral`
(espaços não são aceitos por Git). O plano passa à execução local, com suas
premissas como baseline: consulta anônima, qualidade aditiva, frontend nativo
e homologação local. O backlog condicionado continua fora das 25 tarefas.
A solicitação inclui implementação, testes, commits locais e revisão por
agentes; não inclui push, implantação pública ou envio de notificações.
