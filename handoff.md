# ClimaPrev - Handoff de retomada

Data: 2026-08-29
Estado: **Task 9 concluída e aprovada; trabalho pausado.**

## Estado técnico

O backend MVP FastAPI está implementado como monólito modular stateless, com:

- `GET /api/v1/risk` por texto ou coordenadas, período de até sete dias;
- seleção de `temperature_unit=celsius|fahrenheit`, com cálculo canônico em
  Celsius;
- adaptadores Open-Meteo protegidos por portas de aplicação;
- política de risco determinística, versionada e explicitamente heurística;
- `official_alerts` separado e `not_configured`;
- Redis para cache, stale fallback, lock distribuído e rate limit;
- request ID, logs estruturados, métricas e health checks;
- perfil Docker de carga com app FastAPI real, Redis real e mock Open-Meteo.

## Evidências

- `docker compose run --rm app pytest -q -W error`: **148 passed**.
- `docker compose run --rm app ruff check src tests`: passou.
- `docker compose run --rm app mypy src`: passou em 32 arquivos.
- Suite de carga: **16 test cases passed**.
- Baseline final: 60.000 requisições em 600 s, 100,14 req/s, p50/p95/p99
  120/160/180 ms, 0 falhas, 0 respostas 5xx e 0 respostas 429.
- Cenários de 30 s: `cold_cache` p95 140 ms, `lock_contention` p95 65 ms,
  `slow_upstream` p95 410 ms e `redis_latency` p95 430 ms; todos sem falhas.
- Revisão independente final: **APPROVED**, sem achados médios ou altos.

Artefatos de evidência:

- `.superpowers/sdd/climaprev-backend-mvp/task-9-baseline-20260829-final.txt`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-scenario-measurements-20260829.txt`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-report.md`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-review.md`

## Documentação de referência

A lista abaixo é somente para leitura e retomada de contexto; não é uma lista
de arquivos para upload. O diretório `.specs/` fica explicitamente fora de
qualquer staging, commit ou push.

Leia, nesta ordem:

1. `.specs/STATE.md`
2. `.specs/features/climaprev-backend-mvp/context.md`
3. `.specs/features/climaprev-backend-mvp/spec.md`
4. `.specs/features/climaprev-backend-mvp/design.md`
5. `.specs/features/climaprev-backend-mvp/tasks.md`
6. `docs/superpowers/plans/climaprev-backend-mvp.md`
7. `.superpowers/sdd/climaprev-backend-mvp/task-9-report.md`
8. `.superpowers/sdd/climaprev-backend-mvp/task-9-review.md`

## Processo na próxima retomada

Siga esta sequência quando o usuário autorizar a retomada:

1. Reabra o workspace `C:\Users\sammt\OneDrive\Documentos\ClimaPrev`.
2. Leia este handoff e os documentos de referência acima.
3. Confirme o estado pausado e o último resultado validado.
4. Aguarde o usuário definir e aprovar o próximo escopo.
5. Crie um brief específico antes de alterar código ou testes.
6. Aplique TDD, implemente com subagentes e execute os testes dentro do Docker.
7. Solicite revisão independente entre as tasks e corrija achados antes de
   avançar.
8. Atualize o relatório da task, `progress.md`, `.specs/STATE.md` e este
   handoff com evidências reais.
9. Pare containers temporários ao finalizar a sessão.

Não iniciar trabalho novo nem despachar subagentes antes da confirmação
explícita do usuário. Não remover volumes, imagens ou arquivos do projeto.

## Git na próxima retomada

O Git passa a fazer parte do fluxo de trabalho a partir da próxima sessão.
Depois de reabrir o terminal, verifique a instalação e o estado do repositório:

```powershell
git --version
git status --short --branch
```

Se `git` ainda não for reconhecido, reabra o terminal para atualizar o `PATH`
antes de continuar. Quando houver um repositório válido, crie ou selecione uma
branch de trabalho, revise o diff e use staging explícito por allowlist.

Não usar `git add .`. O diretório `.specs/` é material de planejamento e
contexto e não deve entrar na lista de arquivos a subir: nunca deve ser
adicionado ao staging, commit ou push. Antes de qualquer commit, conferir:

```powershell
git diff --cached --name-only
```

Se qualquer caminho `.specs/` aparecer, removê-lo do staging e revisar a
allowlist. A revisão e o commit devem ocorrer somente após a confirmação
explícita do próximo escopo pelo usuário.

## Limitações conhecidas

O MVP ainda não inclui integração autorizada de alertas oficiais, autenticação,
histórico persistente, notificações, mapas, frontend, aplicativo mobile ou ML.
O baseline usa um mock determinístico e não representa disponibilidade do
Open-Meteo público nem capacidade de produção.
