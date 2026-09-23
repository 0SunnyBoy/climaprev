# Tasks — implementação da segurança do ClimaPrev

Estado em 2026-09-23: T1–T16 e T18 com implementação e gates locais;
T17 com execução local, mas sem execução remota do workflow; T19 pendente.
Sem prontidão de produção. Nenhuma
rotação real, publicação ou alteração no SIGFAS está autorizada por esta
execução.

Na retomada de 2026-09-23, T14 passou em stack sintética com Redis, TLS,
ACL, coleta de logs e menor privilégio; T15 passou em navegadores HTTP e
HTTPS com CA explícita; T16 passou com regras padrão, uma exceção histórica
por fingerprint e fixtures de detecção; T17 executou os gates localmente,
mas depende do runner GitHub; T18 passou no ensaio sintético de rotação e
tem runbook. Consulte [contexto](context.md) e [evidências](evidence.md).

[Spec](../../../docs/planejamento/seguranca-configuracao-segredos/spec.md) ·
[Design](../../../docs/planejamento/seguranca-configuracao-segredos/design.md).

## Execution Plan

Decisão de implementação recebida. Ordem de execução:

1. Phase 1: T1–T4 — impedir publicação acidental e fechar configuração.
2. Phase 2: T5–T9 — credenciais, IP, Redis e cliente HTTP.
3. Phase 3: T10–T15 — borda, logs, isolamento e frontend.
4. Phase 4: T16–T19 — prevenção no CI, operação e evidências.

Cada tarefa entrega um componente ou arquivo principal, com seus testes no
mesmo lote. Adaptar fixtures afetadas no lote que muda o contrato. Testes
planejados ainda inexistentes estão identificados como novos. Não deixar
testes para uma fase final; T19 apenas reúne evidências já produzidas.

Antes de começar: registrar HEAD/diff, conferir alterações concorrentes,
confirmar execução Docker/Podman permitida e usar somente dados sintéticos.
Segredos encontrados no SIGFAS exigem triagem separada pelo proprietário;
essas correções não fazem parte das tarefas ClimaPrev.

### Diagrama de dependências

```text
T1 -> T2
T1 -> T3 -> T4
T4 -> T5
T4 -> T6
T5 -> T7
T6 -> T7
T4 -> T8
T7 -> T8
T4 -> T9
T8 -> T9
T6 -> T10
T9 -> T10
T10 -> T11 -> T12
T3 -> T13
T10 -> T13
T5 -> T14
T8 -> T14
T11 -> T14
T12 -> T14
T10 -> T15
T11 -> T15
T13 -> T15
T14 -> T15
T1 -> T16
T2 -> T16
T9 -> T17
T13 -> T17
T14 -> T17
T15 -> T17
T16 -> T17
T14 -> T18
T17 -> T18
T17 -> T19
T18 -> T19
```

## Test Coverage Matrix

Gerada a partir do código, da spec, do
[pyproject](../../../pyproject.toml),
do [CI](../../../.github/workflows/ci.yml)
e do [guia de homologação](../../../docs/operacoes/homologacao.md).
Não foi encontrado CONTRIBUTING ou AGENTS próprio no worktree. Não há
percentual mínimo configurado nesses arquivos; usar cobertura por critério
e caso-limite, sem inventar uma meta de cobertura já existente.

Amostras: testes de segredo Redis, destinos, proxy/cota, falhas de logging,
runtime, retenção, imagem e scripts de homologação existentes. Padrão:
pytest com async/respx para backend e scripts Docker para topologia real.

| Code Layer                 | Required Test Type                        | Coverage Expectation                                                                                | Location Pattern                                                                           | Run Command             |
| -------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------- |
| Configuração e secrets     | Unit + integração de startup              | Cada ramo de aceitação/rejeição e ausência de valores em dumps/erros; SEC-01, CFG-01                | `tests/unit/test_*secret*.py`, `tests/unit/test_*config*.py`, novos testes de configuração | Quick + Full            |
| Proxy e pseudonimização    | Unit + API + Redis real                   | IPv4/IPv6, spoofing, fallback, concorrência/TTL, quotas entre workers                               | `tests/unit/api/`, `tests/integration/api/`, `tests/integration/redis/`                    | Quick + Full            |
| Cliente externo            | Unit/integration respx/stream             | Happy path, redirects, bytes, compressão, deadline, retries e cancelamento                          | `tests/integration/providers/`, novo teste de cliente HTTP                                 | Full                    |
| Redis/ACL                  | Integração no container protegido         | Senha válida/inválida/ausente; namespace; Lua; comandos proibidos; locks/cache/budget               | `tests/docker/check_homolog_redis.py` e testes novos de provisionamento                    | Homolog + Full          |
| Nginx/Compose/build        | Estático + smoke real                     | Rotas, método, Host, TLS, headers em erro, arquivos ocultos, mounts, UID, rede, imagem e sentinelas | `tests/docker/`                                                                            | Build + Local + Homolog |
| Logs                       | Unit + subprocess + integração de entrada | Todos os canais sensíveis; whitelist; teto/reinício de retenção                                     | `tests/unit/test_log_retention.py`, `tests/docker/test_runtime_logging.py` e smokes        | Full + Homolog          |
| Frontend público           | Browser + HTTP de aceitação               | Conteúdo malicioso inerte, mesma origem, sem segredo em assets/storage/rede                         | Novo `tests/docker/check_frontend_security.py`                                             | Browser                 |
| Scanner/CI                 | Fixture temporária positiva/negativa      | Segredo sintético bloqueia, exemplo seguro passa, erro do scanner bloqueia; saída redigida          | Novos testes em `tests/docker/` e workflow de segurança                                    | Security                |
| Procedimentos/documentação | Inspeção + ensaio local                   | Passos reproduzíveis, nova senha aceita/antiga recusada, sem dados reais                            | Docs operacionais e evidência final                                                        | Docs + Homolog          |

## Gate Check Commands

Executar a partir de `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3`.
Comandos abaixo são a matriz planejada; as execuções realmente recebidas
estão em `evidence.md`. Não mostrar `docker compose config` completo, `env`, conteúdo de
secrets ou inspeções que exponham valores. Usar `config --quiet`.

| Gate Level | When to Use                                                             | Command                                                                                                                                                                       |
| ---------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Docs       | Qualquer mudança documental                                             | `git diff --check` e revisão de referências/requisitos; validadores abaixo                                                                                                    |
| Quick      | Unitários                                                               | `docker compose run --rm app pytest -q -W error tests/unit`                                                                                                                   |
| Full       | Integração/contratos                                                    | `docker compose run --rm app pytest -q -W error`                                                                                                                              |
| Build      | Fim de fase executável                                                  | `docker compose config --quiet`, `docker compose build app`, Full, `docker compose run --rm app ruff check src tests --ignore EXE002`, `docker compose run --rm app mypy src` |
| Local      | Proxy local após subir stack isolada                                    | `docker compose exec -T frontend nginx -t`; executar smokes locais atualizados na tarefa                                                                                      |
| Homolog    | Após provisionar diretório de teste e subir stack dedicada              | `python3 tests/docker/check_homolog_tls.py`, `python3 tests/docker/check_homolog_frontend.py`, `python3 tests/docker/check_homolog_topology.py`; Redis pelo método abaixo     |
| Browser    | Depois de T15, usando o runner pinado; T17 o reutiliza no CI            | `python tests/docker/check_frontend_browser.py --base-url http://127.0.0.1:8080`; HTTPS exige `--ca-file` e perfil Firefox temporário |
| Security   | Depois de T16/T17, com binários pinados                                 | `gitleaks git --redact --config .gitleaks.toml .`; scan da imagem por Trivy configurado em T17; fixtures do scanner                                                           |

Smoke Redis atual, que T5/T14 precisam adaptar ao novo namespace:

```bash
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml exec -T app python - < tests/docker/check_homolog_redis.py
```

O redirecionamento fornece somente script de teste, não conteúdo de segredo.
Não usar `compose run app` com a stack de homologação já ativa: o endereço
fixo pode conflitar. Seguir provisionamento do guia existente em diretório
novo; não sobrescrever `.homolog` existente nem remover volumes alheios.

Validação estrutural dos documentos, se a skill estiver disponível:

```bash
python3 /home/ney/.codex/skills/tlc-spec-driven/scripts/validate_spec.py docs/planejamento/seguranca-configuracao-segredos/spec.md --strict
python3 /home/ney/.codex/skills/tlc-spec-driven/scripts/validate_tasks.py docs/planejamento/seguranca-configuracao-segredos/tasks.md --strict
```

O check Docs não substitui a execução dos gates funcionais. Se o engine não
estiver disponível, registrar bloqueio e testes não executados, sem marcar
a tarefa como concluída. Não iniciar provedores reais para contornar mocks.

## Task Breakdown

### Phase 1 — configuração e prevenção de publicação

### T1: Proteger variantes de configuração no Git

**What**: Acrescentar exclusão de `.env.*`, preservar `.env.example` e `.homolog/`; detectar arquivos já rastreados sem removê-los automaticamente.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/.gitignore`
**Depends on**: none
**Reuses**: Regras atuais de exclusão, sem modificar arquivos locais de segredo.
**Requirement**: GIT-01.
**Tests**: Novo `tests/docker/check_secret_file_policy.py`: `git check-ignore --no-index` para nomes sintéticos na raiz/subpastas, exemplo permitido e tracking consultado só por nomes.
**Gate**: Docs + teste específico em clone/fixture temporária; não requer leitura de `.env`.
**Done when**: Regras comprovadas para todos os casos de GIT-01; valores reais não aparecem em saída e nenhuma alteração alheia é removida.

### T2: Impedir segredos no contexto e artefatos

**What**: Excluir variantes de `.env` e material privado também dentro de diretórios permitidos pelo build, preservando a allowlist.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/.dockerignore`
**Depends on**: T1
**Reuses**: Deny-by-default e testes existentes de runtime/package.
**Requirement**: BUILD-01.
**Tests**: Ampliar `tests/docker/test_package_assets.py` e `check_runtime_image.py`; sentinelas sintéticas em fixture isolada devem ficar fora do contexto efetivo, layers, wheel e imagem final.
**Gate**: Build + smoke de imagem em contexto temporário controlado.
**Done when**: Artefatos continuam funcionais e nenhuma sentinela é encontrada; não depender apenas de busca no working tree.

### T3: Documentar variáveis e fontes sem valores reais

**What**: Atualizar exemplo com nomes, finalidade, obrigatoriedade por perfil e caminhos de secrets; diferenciar password, cache key, IP interno e URL pública.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/.env.example`
**Depends on**: T1
**Reuses**: Contrato D2 e exemplo atual; não copiar `.env` real nem credenciais SIGFAS.
**Requirement**: CFG-01, SEC-01.
**Tests**: Novo teste de contrato do exemplo em `tests/docker/check_secret_file_policy.py`: nomes conhecidos, nenhum segredo e configuração local sem exigir chave real em checkout limpo.
**Gate**: Docs + teste específico.
**Done when**: Exemplo não sugere senha no frontend/URL; campos novos estão marcados como implementados somente quando T4 existir.

### T4: Fechar validação e carregamento dos secrets

**What**: Implementar enum, detecção de aliases Redis divergentes, exigências production, validação de hosts/destinos/limites e chave HMAC privada conforme D2.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/config.py`
**Depends on**: T3
**Reuses**: Settings, SecretStr, PrivateAttr e validadores existentes.
**Requirement**: CFG-01, SEC-01, IP-01, HTTP-01.
**Tests**: Atualizar testes de segredo/destinos/configuração e fixtures production no mesmo lote; testar todos os campos/limites/aliases, arquivo ilegível, URL com query/senha e ausência de valores em repr/dump/erro. Novo teste de startup negativo com secrets sintéticos.
**Gate**: Quick + Full.
**Done when**: `prodution` e produção sem segredo falham; desenvolvimento/test/load continuam explícitos; nenhum teste usa credencial real ou desabilita validação para passar.

### Phase 2 — credenciais, identidade e saída HTTP

### T5: Gerar secrets independentes e ACL mínima

**What**: Estender provisionamento para ambiente validado, senha e HMAC independentes, ACL por namespace e comandos estritamente necessários.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docker/homolog/provision.py`
**Depends on**: T4
**Reuses**: secrets criptográficos, diretório exclusivo, hash da senha na ACL e outputs sem valores.
**Requirement**: SEC-01, REDIS-01, IP-01.
**Tests**: Novo teste de provisionamento com tmp_path, proibição de overwrite, permissões e ausência de segredo em stdout; atualizar `check_homolog_redis.py` para namespace autorizado, Lua/locks/budget positivos e comandos/chaves proibidos negativos.
**Gate**: Quick + smoke Redis isolado; Homolog completa depois de T14.
**Done when**: ACL mínima passa na imagem escolhida; nenhuma senha na CLI, exemplo ou compose.env; arquivos existentes não são alterados.

### T6: Canonicalizar identidade sem confiar em XFF forjado

**What**: Normalizar peer direto e manter algoritmo de cadeia confiável; fallback estável para peer inválido/ausente sem identidade controlada pelo cliente.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/api/deps.py`
**Depends on**: T4
**Reuses**: client_identity, limite de 20 hops e percurso da direita para esquerda.
**Requirement**: PROXY-01.
**Tests**: Ampliar `tests/unit/api/test_deps.py` e `tests/integration/api/test_proxy_quota.py`: IPv6 equivalente, IPv4, peer desconhecido, proxy não autorizado, cadeia inválida/excessiva e prefixo forjado.
**Gate**: Quick + Full.
**Done when**: Forjar cabeçalho não cria nova cota; normalização não agrupa indevidamente dois IPs distintos.

### T7: Pseudonimizar chaves do rate limit

**What**: Acrescentar identity_key privada, HMAC SHA-256 e namespace v2 conforme D4; recusar production sem chave no construtor.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/infrastructure/rate_limit/redis_rate_limiter.py`
**Depends on**: T5, T6
**Reuses**: Mesmo bucket Lua, cálculo de TTL, RateLimitDecision e falha DependencyUnavailable.
**Requirement**: IP-01, REDIS-01.
**Tests**: Ampliar `tests/integration/redis/test_rate_limiter.py` com chave sintética, identidade igual entre instâncias, diferenciação por chave/ambiente, TTL, v1 não produtivo, ausência de IP literal e Redis indisponível; unitários do digest.
**Gate**: Quick + Full.
**Done when**: Cota e Retry-After preservados; produção não grava IP literal; não existe fallback que libera tudo nem flush de migração.

### T8: Integrar política de runtime e Host

**What**: Passar a chave privada ao limiter, configurar TrustedHostMiddleware e HTTPX com trust_env=False; manter portas internas/documentação condicional e contratos de erro.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/main.py`
**Depends on**: T4, T7
**Reuses**: Lifespan, cleanup, middleware CORS e handlers existentes.
**Requirement**: SEC-01, IP-01, HTTP-01, REDIS-01, AUTH-01.
**Tests**: API/lifespan com fixtures: Host permitido/negado, healthchecks internos, same-origin, proxy ambiente ignorado, secrets não expostos, produção sem docs, Redis errado/ausente com falha segura. Adaptar fixtures de integração afetadas.
**Gate**: Full + Build.
**Done when**: Todos os workers recebem mesma chave montada; API pública segue anônima; nenhuma sessão/JWT é adicionada.

### T9: Limitar respostas e duração das chamadas externas

**What**: Ler em stream com contador descomprimido, impor deadline total, recusar redirects e excesso de bytes, fechar recursos mantendo budget e retries existentes.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/infrastructure/http/client.py`
**Depends on**: T4, T8
**Reuses**: AsyncJsonHttpClient, erros de aplicação, respx, timeouts e callbacks de budget.
**Requirement**: HTTP-01.
**Tests**: Novo `tests/integration/providers/test_http_bounds.py`: chunked, gzip, Content-Length enganoso, limite exato/excedido, deadline, cancelamento, 302/429/5xx e limpeza; fixtures representativas de Open-Meteo/INMET sem acesso real.
**Gate**: Full + Build.
**Done when**: Limites definidos são provados, excesso não é retentado, conexão fecha e erros 502/503 não carregam body/URL/segredo.

### Phase 3 — entrada, logs e ambientes

### T10: Restringir entrada local e eliminar acesso bruto nos logs

**What**: Definir rotas/métodos/assets explícitos, negar arquivos internos, limitar body e logs; manter headers e sobrescrita segura de XFF.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docker/frontend/nginx.conf`
**Depends on**: T6, T9
**Reuses**: CSP e proxy existentes, sem alterar frontend funcional.
**Requirement**: WEB-01, LOG-01, HTTP-01, PROXY-01, NET-01, AUTH-01.
**Tests**: Ampliar smokes `check_local_frontend_proxy.py` e `check_frontend_post.py`: endpoints válidos, métodos inválidos, Host, 413, assets reais, .env/.git/config/docs/metrics negados, caminhos codificados, headers em erro e sentinelas ausentes de access/error log.
**Gate**: Local + Full.
**Done when**: Busca/previsão funcionam, todos os aliases internos retornam 404 e nenhum acesso bruto permanece ativo.

### T11: Aplicar paridade segura à entrada TLS

**What**: Replicar política aprovada de rotas/assets/headers/body e habilitar busca de localidades com log normalizado; preservar TLS e trust boundary.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docker/homolog/entrada/nginx.conf`
**Depends on**: T10
**Reuses**: Certificados montados, map de rotas, safe log e negação padrão.
**Requirement**: WEB-01, LOG-01, HTTP-01, PROXY-01, NET-01, AUTH-01.
**Tests**: Ampliar `check_homolog_frontend.py`/`check_homolog_tls.py`: mesma matriz local, query de busca ausente do log, CA correta funciona/CA errada falha e headers em 404/413/502.
**Gate**: Homolog em stack de teste adaptada; sem desabilitar validação TLS.
**Done when**: Homologação não perde busca nem headers, e somente entrada publica porta em loopback.

### T12: Reconhecer busca no coletor sem registrar a consulta

**What**: Acrescentar rota normalizada da busca à whitelist, preservando esquema mínimo, descarte de campos extras e retenção.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/src/climaprev/log_collector.py`
**Depends on**: T11
**Reuses**: LogStore, relógio injetável, limites de mensagem/arquivo e expurgo.
**Requirement**: LOG-01.
**Tests**: Ampliar `tests/unit/test_log_retention.py` e testes de runtime: busca aceita sem args, rotas desconhecidas viram unmatched, token/IP/body extras descartados e arquivos expirados removidos na retomada.
**Gate**: Quick + Full.
**Done when**: Alteração não aumenta cardinalidade nem retenção e nenhum dado enviado como campo extra chega ao arquivo.

### T13: Isolar carga e preservar desenvolvimento

**What**: Criar Redis e rede internal próprios para load; fixar os três destinos no provider-mock, sem herança das URLs reais; manter serviços normais em loopback.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docker-compose.yml`
**Depends on**: T3, T10
**Reuses**: Perfis de carga, cenários, mock e defaults de orçamento existentes.
**Requirement**: LOAD-01, NET-01, PROXY-01.
**Tests**: Atualizar testes de harness/load/topologia: .env sintético com destinos externos não altera app-load; redes/mounts separados; falha do mock não gera fallback real; Redis dev permanece sem alterações causadas por carga.
**Gate**: Build + Local + cenário de carga somente isolado.
**Done when**: app-load e mock não têm rota externa; todos os provedores são mock e dados/cotas não atravessam o Redis de desenvolvimento.

### T14: Integrar endurecimento e secrets na homologação

**What**: Montar chave HMAC apenas no app, explicitar hosts e ACL, pinar imagens e aplicar menor privilégio por serviço; manter logs e topologia privada.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docker-compose.homolog.yml`
**Depends on**: T5, T8, T11, T12
**Reuses**: runtime UID 10001, redes ingress/cache, file secrets, socket e collector sem rede.
**Requirement**: SEC-01, REDIS-01, IP-01, NET-01, PROXY-01, LOG-01.
**Tests**: Ampliar smokes topology/redis/TLS/hardening para mounts por consumidor, leitura real de secrets pelo UID correto, root filesystem read-only, capabilities mínimas, senhas inválidas, isolamento e reinício. Não imprimir inspeção completa dos containers.
**Gate**: Homolog + Full + Build.
**Done when**: App consegue autenticar/limitar; frontend/coletor não leem senha Redis/HMAC; permissões funcionam no engine declarado sem acesso mais amplo que o documentado.

### T15: Provar segurança do frontend público

**What**: Acrescentar componente de aceitação HTTP/browser para a fronteira pública; nenhuma refatoração visual é necessária para este controle.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/tests/docker/check_frontend_security.py` e `tests/docker/check_frontend_browser.py` (novos)
**Depends on**: T10, T11, T13, T14
**Reuses**: Frontend textContent, chamadas relativas e provider-mock; reaproveitar smokes existentes.
**Requirement**: WEB-01, BUILD-01.
**Tests**: Os componentes usam dados sintéticos, nome contendo markup, interceptação de rede, assets e storage; o runner Playwright pinado prova CSS carregado, requisições de mesma origem e DOM inerte. O contrato HTTP também verifica que sentinelas secretas do servidor não aparecem no cliente. Incluir caso que faria o teste falhar.
**Gate**: Browser + Local + Homolog; escolher e validar nesta tarefa um runner Playwright pinado apenas de teste, registrar versão/digest em instruções do componente; T17 reutiliza esse runner sem dependência produtiva nova.
**Done when**: Matriz passa nas duas entradas e usa CA explícita; nenhuma opção ignoreHTTPS ou acesso a provedor real é necessária.

### Phase 4 — CI e operação

### T16: Definir política de detecção de segredos

**What**: Acrescentar configuração de Gitleaks com regras padrão e padrões do projeto; exceções apenas para fixtures precisas e documentadas.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/.gitleaks.toml` (novo)
**Depends on**: T1, T2
**Reuses**: Formatos de secrets e exemplos classificados em D1/D2.
**Requirement**: GIT-01, CI-01.
**Tests**: Novo teste de gate em repo temporário: literal sintético detectado, exemplo seguro aceito e relatório/console redigidos; não criar commit de teste com segredo no repo ClimaPrev.
**Gate**: Security local, com versão pinada e checksums verificados.
**Done when**: Não existem allowlists amplas para docs/tests/.env; código de saída distingue finding, sucesso e falha da ferramenta.

### T17: Acrescentar gate de segurança ao CI

**What**: Criar workflow com histórico suficiente para scanner, auditoria de imagem/dependências e smokes protegidos incluindo browser; preservar CI atual e privilégio mínimo.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/.github/workflows/security.yml` (novo)
**Depends on**: T9, T13, T14, T15, T16
**Reuses**: Comandos existentes pytest/ruff/mypy, locks e imagens; Gitleaks CLI e Trivy com versões/digests revisados.
**Requirement**: CI-01, BUILD-01, LOAD-01, GIT-01.
**Tests**: Fixtures de workflow/gates: segredo sintético bloqueia, HIGH/CRITICAL sem exceção bloqueia, inventário Python não vazio, scanner indisponível bloqueia, PR não recebe secrets; resultado e artefatos não contêm valores. Playwright de teste tem instalação/runner pinado e CA local confiada explicitamente.
**Gate**: Security + Build + Browser + Homolog em execução local/CI autorizada.
**Done when**: Gates necessários passam, findings/exceções têm dono/prazo, actions estão por SHA verificado e nenhum job executa código de PR com credenciais produtivas. Criar workflow local não autoriza push ou mudança de branch protection.

### T18: Documentar e ensaiar operação segura

**What**: Acrescentar inventário sem valores, provisionamento por ambiente, diagnóstico sanitizado, rotação e rollback seguro; registrar limites NAT/host/TLS e a decisão de não adicionar login.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docs/operacoes/segredos-e-seguranca.md` (novo)
**Depends on**: T14, T17
**Reuses**: Guia atual de homologação e D8; atualizar referências cruzadas necessárias como parte do mesmo documento operacional.
**Requirement**: OPS-01, AUTH-01.
**Tests**: Ensaio somente local com dois conjuntos sintéticos: nova senha aceita/antiga recusada, HMAC consistente entre workers, cache frio/cota reiniciada registrados, diretório anterior preservado e nenhuma credencial em evidência.
**Gate**: Docs + Homolog + checklist de rotação.
**Done when**: Outra pessoa consegue executar os passos, rollback não restaura segredo comprometido e o procedimento não promete que .env é cifrado ou que IP público fica invisível.

### T19: Consolidar evidências e decisão de prontidão

**What**: Registrar resultados por requisito, comandos/versões, falhas e pendências; revisar independência dos controles e impedir declaração de produção pronta sem verificar o ambiente real.
**Where**: `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3/docs/planejamento/seguranca-configuracao-segredos/evidence.md` (novo, somente após execução)
**Depends on**: T17, T18
**Reuses**: Evidências redigidas das tarefas; não recriar testes em uma fase tardia.
**Requirement**: CI-01, OPS-01 e confirmação de todos os requisitos da spec.
**Tests**: Reexecutar matriz de regressão em checkout/stack isolados; revisão independente de rastreabilidade, artefatos sem sentinelas e status de cada gate.
**Gate**: Docs + Full + Build + Local + Homolog + Browser + Security.
**Done when**: Cada requisito está verified ou explicitamente bloqueado; para declarar implementação completa nenhum gate obrigatório fica pendente. DNS/firewall/certificado público não verificados impedem declarar prontidão de publicação.

## Diagram-Definition Cross-Check

| Task | Depends on (definição = diagrama) | Phase | Deliverable único        |
| ---- | --------------------------------- | ----- | ------------------------ |
| T1   | none                              | 1     | Exclusão Git             |
| T2   | T1                                | 1     | Exclusão Docker          |
| T3   | T1                                | 1     | Exemplo de configuração  |
| T4   | T3                                | 1     | Settings                 |
| T5   | T4                                | 2     | Provisionador            |
| T6   | T4                                | 2     | Resolvedor de identidade |
| T7   | T5, T6                            | 2     | Rate limiter             |
| T8   | T4, T7                            | 2     | Composição do runtime    |
| T9   | T4, T8                            | 2     | Cliente HTTP             |
| T10  | T6, T9                            | 3     | Entrada local            |
| T11  | T10                               | 3     | Entrada TLS              |
| T12  | T11                               | 3     | Coletor                  |
| T13  | T3, T10                           | 3     | Compose local/load       |
| T14  | T5, T8, T11, T12                  | 3     | Compose homolog          |
| T15  | T10, T11, T13, T14                | 3     | Aceitação frontend       |
| T16  | T1, T2                            | 4     | Configuração do scanner  |
| T17  | T9, T13, T14, T15, T16            | 4     | Workflow segurança       |
| T18  | T14, T17                          | 4     | Runbook                  |
| T19  | T17, T18                          | 4     | Relatório de evidências  |

## Test Co-location Validation

| Tasks   | Camada e teste no mesmo lote                            | Confirmação de cobertura planejada                        |
| ------- | ------------------------------------------------------- | --------------------------------------------------------- |
| T1–T3   | Políticas de arquivo + testes de nomes/contexto/exemplo | Positivo, negativo, variante em subpasta e artefato final |
| T4      | Settings + unitários/startup/fixtures                   | Todos os critérios CFG/SEC e casos-limite                 |
| T5      | Provisionador + permissões/ACL real                     | Senha, namespace, comandos e Lua                          |
| T6–T8   | API/limiter/runtime + unit/API/Redis                    | Spoofing, IP canônico, HMAC, multiworker e falha segura   |
| T9      | HTTP + stream/mocks                                     | Bytes, tempo, redirects, retries e cancelamento           |
| T10–T11 | Nginx + smoke das mesmas entradas                       | Rotas, headers, TLS, logs e arquivos proibidos            |
| T12     | Coletor + retenção/sanitização                          | Whitelist, tamanho e reinício                             |
| T13–T14 | Compose + topologia/hardening                           | Sem egress load, sem portas internas, secrets por serviço |
| T15     | Componente de aceitação + fixtures positivas/negativas  | Execução de script e segredo visível devem ser detectados |
| T16–T17 | Scanner/workflow + fixtures                             | Bloqueio real e redação sem credenciais produtivas        |
| T18     | Runbook + ensaio sintético                              | Senha antiga recusada e procedimento reproduzível         |
| T19     | Evidências + reexecução dos gates anteriores            | Sem status aprovado para teste não executado              |

## Status desta entrega

O usuário aprovou implementação e testes locais. Os status finais dependem
dos gates e da revisão independente; código escrito não significa verificado.
Lote T1–T9 pausado com validação parcial. As alterações anteriores do usuário
são preservadas. Não houve resultado final do agente auxiliar antes da parada.

SPEC_DEVIATION: commits por tarefa adiados durante a integração porque a
árvore já contém mudanças do usuário nos mesmos arquivos. Não agrupar nem
versionar essas mudanças automaticamente. Posteriormente, o usuário autorizou
um checkpoint Git da segurança e do contexto para outro Codex. Essa exceção
não inclui mudanças anteriores de frontend/Compose/documentação geral, deploy,
revogação de segredo real ou reescrita de histórico.
