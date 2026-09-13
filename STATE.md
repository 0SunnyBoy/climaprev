# STATE — Clima Prev

**Atualização:** 2026-09-13. **Branch:** `atualizaçao-geral`.
[Índice](PROJECT.md) · [Tarefas](docs/planejamento/evolucao-climaprev/tasks.md).

## Execução atual

As 25 tarefas foram implementadas e commitadas pelos agentes. T25 fechou
em `d5a7e21`; a verificação independente final é a próxima etapa. Push e publicação não integram o pedido.

- T1–T10, `backend_dados_resiliencia`: fuso efetivo, validação, completude,
  média de temperatura, cache v2, expiração na entrega, corrupção, falhas,
  propriedade do lock e configuração numérica.
- T11–T20, `preflight_operacao`: destinos permitidos, proxies e cotas, logs
  sanitizados, métricas por processo, dependências com hashes, runtime sem
  privilégios e homologação local protegida.
- T21–T25, `interface_consulta`: formulário, consulta assíncrona, previsão,
  qualidade/risco/alertas separados, recuperação, cancelamento, teclado e
  layout móvel. Commits: `acd8d08`, `497363a`, `5b89ef0`, `63e6a91`
  e `d5a7e21`.

## Evidências executadas

- Baseline da sessão: 148 testes aprovados.
- T10: 267 testes, build, Ruff e mypy em 34 arquivos aprovados.
- T20 (`73c8fb5`): 312 testes, builds dev/runtime, Ruff e mypy em 39
  arquivos aprovados; provas reais de TLS, Redis/ACL, isolamento e logs.
- Fechamento da interface (`d5a7e21`): 316 testes aprovados em 47,53 s; Ruff, mypy em
  39 arquivos, builds, assets no runtime e roteiro B01–B10 aprovados.
- Browser HTTPS: rejeição sem CA e sucesso com CA explícita em perfil
  temporário; `/internal/metrics` permanece 404 na entrada. Nenhum bypass
  TLS ou alteração da confiança global do navegador.
- Falhas iniciais do teste de logs ocorreram antes da prontidão do processo.
  O harness agora aguarda até 10 s e falha explicitamente se o runtime não
  iniciar; as assertions de sanitização foram preservadas. A suíte final
  passou e as tentativas estão registradas na evidência T25.

A revisão independente ainda está pendente. Testes com fixtures não indicam
capacidade ou disponibilidade do Open-Meteo público. Não houve validação
científica nova da política de risco.

## Prévia e operação local

- Interface: `http://127.0.0.1:18000`, contêiner `climaprev-ui-browser`, com
  fontes atuais montadas. Para encerrar somente a prévia:
  `docker rm -f climaprev-ui-browser`.
- Homologação: `https://localhost:18443`; procedimentos, CA e limites em
  [homologacao.md](docs/homologacao.md). API e Redis sem portas diretas.
- Docker usa Podman rootless. Redis do projeto `climaprev` foi criado nesta
  sessão e permanece para testes/prévia. O app da homologação usa IP fixo;
  provas usam `compose exec -T app`, evitando conflito com `compose run`.
- Podman não preserva necessariamente o IP externo original e ignora
  uid/gid/mode de file secrets; permissões foram verificadas na stack local.
- Preservar `.harness-eval/`, `.notebook/` e a formatação preexistente do
  Compose. Diff inicial: `/tmp/climaprev-preexisting-compose.diff`.

## Escopo condicionado

Alertas oficiais permanecem `not_configured`. Contas, histórico, notificações,
validação científica da política e implantação pública exigem escopo próprio.
A documentação SIGFAS foi usada como modelo; não há integração entre sistemas.
O [handoff histórico](handoff.md) permanece como registro anterior.
