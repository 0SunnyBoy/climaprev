# STATE — Clima Prev

**Atualização:** 2026-09-13. **Branch:** `atualizaçao-geral`.
[Índice](PROJECT.md) · [Tarefas](docs/planejamento/evolucao-climaprev/tasks.md).

## Execução atual

O usuário autorizou implementação local e coordenação de agentes para concluir
as 25 tarefas. T1–T10 estão concluídas; T11–T20 são o próximo bloco, seguidas
por T21–T25 e verificação independente. Push e publicação não integram o pedido.

Entregues: fuso efetivo, validação de dados, completude, média de temperatura,
identidade v2 do cache, expiração na entrega, tratamento de corrupção/erros,
controle de perda de lock e validação numérica da configuração.

## Evidência

- Baseline executado nesta sessão: 148 testes aprovados.
- Fechamento T10: 267 testes aprovados, 82 no gate unitário, build e Ruff
  aprovados; mypy aprovou 34 arquivos.
- Commits do bloco: `b906b92`, `b766d45`, `626439a`, `58374de`, `c4731f8`,
  `1e6f101`, `2e1d364`, `2888517`, `a64bdfd`, `9d2993c`.
- Evidências por tarefa em [evidence](docs/planejamento/evolucao-climaprev/evidence/t10.md).
- A validação independente final ainda não ocorreu. Esses resultados não
  representam capacidade ou disponibilidade do provedor público.

## Continuidade

- Agente do bloco concluído: `backend_dados_resiliencia`.
- Próximo: `preflight_operacao`, T11–T20; depois novo agente para T21–T25.
- Docker usa Podman rootless. Redis do projeto `climaprev`, criado nesta sessão,
  deve permanecer até a verificação final. Testes usam imagem atualizada ou
  source/tests atuais montados somente leitura.
- Chrome `/usr/bin/google-chrome` e Playwright da skill `playwright-skill`
  estão disponíveis; lançamento visível já validado.
- O preflight confirmou TLS com CA, montagem readonly e rede interna; o
  Podman ignora uid/gid/mode de file secrets e traduz o IP de origem do host.
  A implementação deve usar permissões verificadas e documentar a limitação.
- Preservar `.harness-eval/`, `.notebook/` e a formatação preexistente do Compose
  (diff inicial em `/tmp/climaprev-preexisting-compose.diff`).

## Escopo condicionado

Frontend e stack protegida aguardam seus blocos de implementação. Alertas
oficiais permanecem `not_configured`. Contas, histórico, notificações,
validação científica da política e implantação pública exigem escopo próprio.
A documentação SIGFAS foi usada como modelo; não há integração entre sistemas.
O [handoff histórico](handoff.md) permanece como registro anterior.
