# STATE — Clima Prev

**Atualização:** 2026-09-13. **Branch:** `atualizaçao-geral`.
[Índice](PROJECT.md) · [Tarefas](docs/planejamento/evolucao-climaprev/tasks.md).

## Execução atual

O usuário autorizou implementação local e coordenação de agentes para concluir
as 25 tarefas. T1–T20 estão concluídas; T21–T25 estão em implementação, seguidas
pela verificação independente. Push e publicação não integram o pedido.

Entregues: fuso efetivo, validação de dados, completude, média de temperatura,
identidade v2 do cache, expiração na entrega, tratamento de corrupção/erros,
controle de perda de lock e validação numérica da configuração. O segundo
bloco acrescentou limites de confiança e cotas, logs sanitizados, métricas
por processo, dependências verificáveis e homologação local protegida.

## Evidência

- Baseline executado nesta sessão: 148 testes aprovados.
- Fechamento T10: 267 testes aprovados, 82 no gate unitário, build e Ruff
  aprovados; mypy aprovou 34 arquivos.
- Commits do bloco: `b906b92`, `b766d45`, `626439a`, `58374de`, `c4731f8`,
  `1e6f101`, `2e1d364`, `2888517`, `a64bdfd`, `9d2993c`.
- Evidências por tarefa em [evidence](docs/planejamento/evolucao-climaprev/evidence/t10.md).
- Fechamento T20 (`73c8fb5`): 312 testes aprovados, Ruff, mypy em 39
  arquivos e builds dev/runtime aprovados. Provas reais de TLS, Redis
  autenticado, isolamento, UID 10001 e retenção/reconexão de logs aprovadas.
- A validação independente final ainda não ocorreu. Esses resultados não
  representam capacidade ou disponibilidade do provedor público.

## Continuidade

- Bloco T1–T10: `backend_dados_resiliencia`, concluído.
- Bloco T11–T20: `preflight_operacao`, concluído. Homologação mantida em
  `https://localhost:18443`, com CA local explícita e procedimentos em
  [homologacao.md](docs/homologacao.md).
- Bloco T21–T25: `interface_consulta`, em implementação.
- Root revisou T13 e identificou falta de metadados em exceções inesperadas500;
  correção/teste SEC02 incluídos pelo agente em T20.
- Browser TLS sintético PASS com CA explícita em perfil descartável Chrome152,
  sem bypass e sem instalar CA no perfil habitual. Script em
  `/tmp/playwright-test-climaprev-ca-trust.js`; repetir contra stackreal em T25.
- Docker usa Podman rootless. Redis do projeto `climaprev`, criado nesta sessão,
  deve permanecer até a verificação final. Testes usam imagem atualizada ou
  source/tests atuais montados somente leitura.
- Chrome `/usr/bin/google-chrome` e Playwright da skill `playwright-skill`
  estão disponíveis; lançamento visível já validado.
- O preflight confirmou TLS com CA, montagem readonly e rede interna; o
  Podman ignora uid/gid/mode de file secrets e traduz o IP de origem do host.
  As permissões foram verificadas e a limitação está documentada.
- Preservar `.harness-eval/`, `.notebook/` e a formatação preexistente do Compose
  (diff inicial em `/tmp/climaprev-preexisting-compose.diff`).

## Escopo condicionado

Frontend está em implementação; a stack protegida foi verificada localmente. Alertas
oficiais permanecem `not_configured`. Contas, histórico, notificações,
validação científica da política e implantação pública exigem escopo próprio.
A documentação SIGFAS foi usada como modelo; não há integração entre sistemas.
O [handoff histórico](handoff.md) permanece como registro anterior.
