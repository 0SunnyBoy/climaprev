# Contexto de retomada — segurança do ClimaPrev

Atualização: 2026-09-21. Implementação interrompida pelo usuário; checkpoint
solicitado para que outro Codex possa concluir o serviço posteriormente.
Branch exata: `Atualizacao-Geral-V3`, no repositório `0SunnyBoy/climaprev`.
Base anterior ao checkpoint: `0a4654e096ab01130ac6bafafa2e5d4a8b28ccf6`.

## Leia primeiro

1. Este contexto e as [evidências reais](evidence.md).
2. [Spec](spec.md): requisitos e critérios de aceite.
3. [Design](design.md): contratos e comparação com o SIGFAS.
4. [Tasks](tasks.md): T1–T19, dependências e gates.
5. O diff do checkpoint e o estado do checkout em que você vai trabalhar.

Os números de testes de ciclos anteriores em `docs/projeto/STATE.md` e nos
documentos de evolução não aprovam a segurança nova. Não existe relatório
final de verificação independente deste ciclo.

## Pedido e limites de autorização

O usuário solicitou usar a análise do SIGFAS como referência para proteger
configuração, senhas, IPs, Redis, HTTP e logs do ClimaPrev. Foram criados spec,
design e tasks, e iniciada a implementação local em lotes sequenciais.
Depois, o usuário pediu para parar. O agente auxiliar e os serviços
temporários de teste foram encerrados.

O pedido posterior autoriza documentar e enviar essas alterações à branch
remota V3, sem concluir novas funcionalidades neste checkpoint. Retome código
somente quando houver pedido para continuar a implementação. Não há
autorização para deploy, rotação real, alterações no SIGFAS, reescrita do
histórico, mudanças de branch protection ou introdução de autenticação.

Consulta pública continua anônima: não adicionar JWT, sessões, Keycloak,
usuários ou banco SQL. `.env` não é criptografia; somente `.env.example`
deve ser versionado. Produção exige arquivos de segredo montados, não
credenciais no frontend, imagem, URL ou variável literal de senha.

## Escopo deste checkpoint

Inclui a implementação parcial T1–T9, testes associados, planejamento e
documentação de retomada. Não representa aceite de nenhuma tarefa cujo gate
obrigatório ainda não passou.

| Área            | Alterações já escritas                                                                                        | Limite atual                                                     |
| --------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Git/build       | `.gitignore` e `.dockerignore` excluem variantes de `.env` e material privado; somente exemplo raiz permitido | Reexecutar prova de contexto, layers, wheel e imagem             |
| Configuração    | `.env.example` ampliado; `Settings` valida ambientes, aliases Redis, hosts, destinos e limites                | Integração dos campos no Compose ainda pendente                  |
| Segredos        | Produção exige senha Redis e HMAC de 32 bytes por arquivos; atributos privados e omissão em representações    | Não houve leitura, troca ou publicação de credencial real        |
| Provisionamento | Senha e HMAC gerados independentemente; ACL por ambiente; sem overwrite                                       | Smoke ACL real e homologação completa precisam ser reconfirmados |
| Identidade      | IP canônico, política de proxy confiável e fallback estável                                                   | Preservar testes de spoofing e limites de cadeia                 |
| Rate limit      | HMAC SHA-256 no namespace v2; produção rejeita ausência da chave                                              | Não fazer flush de migração; v1 apenas não produtivo             |
| Runtime         | `TrustedHostMiddleware`, passagem do HMAC e HTTPX `trust_env=False`                                           | Definir hosts e mounts nos perfis operacionais                   |
| HTTP            | Stream com limite de bytes descomprimidos, deadline total e rejeição de redirects                             | Reexecutar regressão e provas de limpeza/cancelamento            |

Arquivos centrais: `src/climaprev/config.py`, `src/climaprev/api/deps.py`,
`src/climaprev/main.py`, `src/climaprev/infrastructure/http/client.py`,
`src/climaprev/infrastructure/rate_limit/redis_rate_limiter.py` e
`docker/homolog/provision.py`.

Testes novos: `tests/conftest.py`, `tests/security_fixtures.py`,
`tests/unit/test_security_config.py`,
`tests/unit/infrastructure/test_ip_hmac.py`,
`tests/integration/api/test_security_runtime.py`,
`tests/integration/providers/test_http_bounds.py` e os três scripts
`tests/docker/check_secret_{file_policy,provision,build}.py`.
Também foram adaptadas fixtures e verificações existentes afetadas pelos
novos contratos.

Os scripts `check_secret_*.py` são gates explícitos de host, não entram na
descoberta padrão de pytest. A imagem de desenvolvimento não contém todos
os recursos Git/provisionamento que esses gates usam. T17 deve executá-los
explicitamente. Quatro smokes de frontend tiveram somente a remoção de um
shebang incompatível com o modo 0644 para corrigir Ruff EXE001; isso não
implementa T10/T11.

### Alterações anteriores fora deste envio

A árvore já continha alterações de outra etapa. Elas foram preservadas,
mas excluídas do checkpoint de segurança:

- `README.md`, `docker-compose.yml` e `docker-compose.homolog.yml`.
- `frontend/api.js`, `app.js`, `index.html`, `result.js` e `styles.css`.
- Documentos em `docs/arquitetura/`, `docs/frontend/` e os documentos
  operacionais já modificados antes deste trabalho.
- Contexto, spec, tasks e evidências do ciclo `evolucao-climaprev`.
- `docs/projeto/PROJECT.md`, `ROADMAP.md`, `docs/seguranca/seguranca.md`
  e o estudo de possível ampliação de escopo de previsão.

O exemplo de configuração e os arquivos da implementação de segurança foram
incluídos como unidades coerentes com seus testes. Não foi feito `git add .`.
As medições anteriores ocorreram na árvore local, que também continha as
mudanças excluídas. Portanto, um clone do checkpoint precisa de validação
própria; não atribuir aqueles resultados automaticamente ao snapshot remoto.

## Resultados conhecidos no ponto de parada

| Verificação                                         | Resultado observado                                                    | Interpretação                                                           |
| --------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Baseline backend anterior às mudanças               | 333 testes passaram com Redis 8.0.5 nativo e Redis 7.4.11 em container | Referência, não aceite do código novo                                   |
| Baseline `tests/docker`                             | 18 testes passaram separadamente                                       | Não foi uma execução única de 351 testes                                |
| Última regressão completa recebida após as mudanças | 419 passaram, 14 falharam, total 433                                   | Não houve confirmação de suíte integralmente verde antes da interrupção |
| Política de arquivos e provisionamento              | 17 testes passaram                                                     | Dois scripts explícitos de host                                         |
| Ruff                                                | Passou com `--ignore EXE002`                                           | Cinco shebangs incompatíveis foram removidos, sem suprimir novas regras |
| Mypy                                                | Passou em 41 arquivos de origem                                        | Não substitui testes funcionais                                         |
| Spec/tasks e diff                                   | Validadores estritos sem erros/avisos; `git diff --check` passou       | Validação documental/estática                                           |
| Prova exploratória Firefox/CA                       | CA ausente falhou; CA correta no perfil temporário retornou HTTPS 200  | Não é T15 nem validação completa do frontend                            |

As 14 falhas observadas foram de isolamento de cache em
`test_evolution_data.py` (12 casos) e `test_provider_failure_contract.py`
(dois casos). A fixture de `test_end_to_end.py` havia perdido seu `flushdb`
original, enquanto os testes verificam chaves globalmente. Essa limpeza foi
restaurada antes da parada. Ainda falta reexecutar a suíte e comprovar a
correção; não assumir que as falhas desapareceram.

**Risco operacional dos testes:** essa fixture executa `flushdb`. Use
exclusivamente um Redis novo, descartável e dedicado à suíte. Nunca aponte
`REDIS_URL` para desenvolvimento compartilhado, homologação real ou produção.
Essa limpeza de fixture não é autorização para flush em migração de HMAC.

## Vulnerabilidades e decisões pendentes

O Gitleaks 8.30.1 com regras padrão verificou 32 commits e não encontrou
segredos. Isso não substitui T16, o scan do checkpoint ou inspeção de arquivos
ignorados. As regras específicas do projeto ainda não foram implementadas.

Na conferência do checkpoint de 2026-09-21, o scan do snapshot preparado
apontou um falso positivo na lista pública de hosts em `.env.example:18`.
O valor foi inspecionado e não contém segredo. Não foi adicionada supressão;
o resultado com finding permanece registrado em [evidence.md](evidence.md)
e precisa de tratamento preciso e testado em T16.

O Trivy 0.74.0 encontrou na imagem runtime inicial 57 ocorrências HIGH/CRITICAL,
21 CVEs distintos e três ocorrências CRITICAL. O inventário Python tinha
23 pacotes, sem HIGH/CRITICAL nessa execução. Não são resultados da imagem
reconstruída com o checkpoint.

A comparação com a base oficial Python 3.12.14 no digest
`sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`
reduziu para 44 ocorrências HIGH, oito CVEs distintos e zero CRITICAL;
não havia correção indicada para os restantes. A atualização do Dockerfile
foi proposta, mas ficou sem resposta antes da interrupção. Não foi aplicada.
Rever a decisão com o usuário e atualizar a evidência do scanner ao retomar.

Não usar `ignore-unfixed`, exceções genéricas ou rebaixamento de severidade
para tornar o gate verde. A existência de findings não demonstra exploração
remota, mas impede declarar o gate de vulnerabilidades aprovado.

## Ordem para concluir após autorização de retomada

1. Conferir branch, HEAD, diff e alterações concorrentes. Trabalhar em cópia
   isolada quando possível; não importar automaticamente mudanças locais
   anteriores nem copiar segredos do ambiente do usuário.
2. Revisar T1–T9 e executar gates em Redis descartável. Confirmar a correção
   da fixture, ACL real, contexto/layers/wheel e startup positivo/negativo.
3. Implementar T10–T12: políticas de rotas/métodos/assets, body de 16 KiB,
   headers inclusive em erro, logs sem query/IP/segredos e coletor compatível.
4. Implementar T13–T14: Redis e rede exclusivos de carga, três destinos de
   mock sem egress real, versões de imagens verificadas e mounts/hosts de
   homologação. `app-load` precisa constar explicitamente em allowed hosts.
5. Implementar T15: teste de navegador reproduzível nas entradas local/TLS,
   runner pinado de teste, CA explícita em perfil temporário, nenhuma opção
   `ignoreHTTPS`. Confirmar DOM inerte, não somente ausência de execução
   de script, pois CSP pode esconder uma falha de inserção de HTML.
6. Implementar T16–T17: regras do scanner e CI mínimo/pinado, histórico
   suficiente, inventário não vazio, erro de scanner bloqueante e fixtures
   positivas/negativas. Preservar o CI existente, que não faz deploy.
7. Implementar T18–T19: runbook e ensaio de rotação só com dados sintéticos,
   evidência por requisito e revisão independente com casos negativos.
   Não marcar concluído enquanto houver gate obrigatório pendente.

**Atenção imediata à compatibilidade:** o backend novo exige, em production,
senha Redis, arquivo HMAC e allowed hosts explícitos. O Compose de homologação
ainda precisa integrar os novos campos/mounts. Não tentar publicar ou
apresentar a homologação como funcional antes de T14 e seus testes.

### Comandos de referência

Execute a partir da raiz de um checkout isolado, com Python 3.12 e
dependências de teste instaladas conforme `pyproject.toml` e os locks.
Antes do primeiro comando, configure `REDIS_URL` para o Redis descartável
dedicado e confira que nenhum alias `CLIMAPREV_REDIS_URL` conflita com ele:

```bash
pytest -q -W error
pytest -q -W error tests/docker/check_secret_file_policy.py tests/docker/check_secret_provision.py
ruff check src tests --ignore EXE002
mypy src
git diff --check
```

O gate de imagem é separado e requer engine disponível:

```bash
python tests/docker/check_secret_build.py
```

Esse script usa arquivos rastreados pelo Git: execute a partir do checkpoint
completo, não de uma cópia onde testes novos estejam fora do tracking.
Os comandos acima são instruções de retomada, não afirmações de execução
bem-sucedida neste checkpoint. Consulte `tasks.md` para os demais gates.

## Ambiente anterior e reprodutibilidade

A execução anterior usou Docker CLI sobre Podman rootless. Containers sem
limite explícito receberam `pids.max=1`; Redis só iniciou com
`--pids-limit 128`, e o runner usou 256. Não desabilitar seccomp ou isolamento
para contornar isso. O buildx precisou de `docker build --load` para carregar
a imagem localmente.

A alternativa nativa usou Redis somente em loopback, porta 16379, sem
persistência, e HOSTALIASES por processo para o nome `redis`. Não houve
alteração global de DNS ou de `/etc/hosts`. Os serviços temporários foram
parados; nomes, PIDs, imagens e arquivos em `/tmp` não são pré-requisitos de
retomada. Em 2026-09-21, o diretório temporário de ferramentas/relatórios já
não estava disponível. Recrie evidências; não invente links para esses logs.

Foi possível usar Playwright 1.63.0/Firefox 155.0 com CA de teste importada
via certutil em perfil isolado. Isso é uma pista de implementação para T15,
não uma dependência produtiva nem uma alteração do trust store do usuário.

Os únicos sistemas SIGFAS consultados foram cópias locais, como referência
estática: backend base `3777f23b` e frontend base `a778e8b`. Os caminhos no
design identificam essas evidências locais; não fazem parte deste repositório.
Na ausência dessas cópias, use a análise registrada sem afirmar nova revisão.
Não repetir os padrões inseguros encontrados, nem testar credenciais reais.

## Critério de encerramento

O próximo Codex deve atualizar tasks/evidence e produzir a revisão final com
o que foi realmente executado. Separar implementação local, aprovação dos
gates e prontidão de implantação. DNS, firewall, certificado público e
credenciais produtivas não foram verificados. Nenhum resultado histórico
autoriza declarar produção pronta ou promover este checkpoint diretamente.
