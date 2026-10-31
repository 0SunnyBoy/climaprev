# Contexto — evolução do Clima Prev

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Data do baseline:** 2026-09-13. **Estado do documento:** planejamento inicial;
o estado atual está em [STATE](../../projeto/STATE.md), atualizado em 20/10/2026.
**Branch vigente:** `develop`; `Atualizacao-Geral-V3` pertence ao histórico. O planejamento começou em
`docs/plano-evolucao-climaprev`, a partir de `main`, commit `a010c3b`.
As alterações locais anteriores foram preservadas.

As referências à branch e ao commit nas seções históricas abaixo descrevem o
baseline de 13 de setembro. Elas não substituem o estado atual registrado em
`STATE.md`.

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
| [PROJECT](../../projeto/PROJECT.md)            | Limites do produto e mapa do código.                    |
| [Arquitetura](../../arquitetura/arquitetura.md)       | Reutilizar API, aplicação, domínio e adaptadores.       |
| [Fluxos](../../arquitetura/fluxos.md)                 | Atualização concorrente, stale e erros.                 |
| [Informações](../../arquitetura/fluxos-informacao.md) | Contrato HTTP e dados que cruzam fronteiras.            |
| [Segurança](../../seguranca/seguranca.md)           | Controles existentes e pendências PEN-01 a PEN-09.      |
| [Restrições](../../operacoes/restricoes.md)         | Qualidade, fuso, limites e interpretação da estimativa. |
| [ROADMAP](../../projeto/ROADMAP.md)            | R1/R2 como base, R3 de preparação e R4 de interface.    |
| [STATE](../../projeto/STATE.md)                | Separar histórico de resultados atuais.                 |

## Base inicial confirmada no repositório

- Python 3.12, FastAPI, HTTPX e Redis; testes pytest, respx, Ruff e mypy.
- `GET` e `POST /api/v1/risk`, consulta anônima, período máximo de sete dias.
- `GET /api/v1/locations/search` com até cinco sugestões de localidade.
- `reference-v1`, cálculo em Celsius e conversão apenas na saída.
- Redis para cache, lock e limite por IP; rotas de saúde existentes.
- O frontend inicial estava em construção e a fonte oficial ainda não havia
  sido escolhida neste baseline. Atualmente, o frontend está em `frontend/` e
  o INMET possui integração básica registrada em P2.1.
- Documentos anteriores e formatação de `docker-compose.yml` já estavam no
  diretório de trabalho; não foram descartados ao criar a branch.

## Fronteira do planejamento

Detalhar a evolução local do backend e uma interface pública de consulta.
Preparar o pacote técnico de implantação sem escolher um fornecedor cloud ou
publicar um ambiente. Contas e notificações permanecem no backlog; a
integração básica de alertas oficiais do INMET foi adicionada depois do
baseline, enquanto cobertura e operação ampliadas continuam condicionadas a
contratos e decisões próprias.

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

- **Alertas oficiais:** o baseline previa selecionar fonte, confirmar cobertura,
  contrato, atualização, expiração e tratamento de indisponibilidade. A
  integração básica do INMET foi adicionada depois; cobertura operacional e
  monitoramento ampliados continuam pendentes.
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
de agentes para finalizar as tarefas. A branch usada naquele baseline era
`atualizaçao-geral` (espaços não são aceitos por Git). O plano passa à execução
local, com suas
premissas como baseline: consulta anônima, qualidade aditiva, frontend nativo
e homologação local. O backlog condicionado continua fora das 25 tarefas.
A solicitação inclui implementação, testes, commits locais e revisão por
agentes; não inclui push, implantação pública ou envio de notificações.
