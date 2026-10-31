# Evidências de execução da segurança

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Estado em 2026-09-23: T14–T19 com gates locais aprovados; T17 também
aprovado no GitHub Actions. T19 concluiu com decisão condicional. Sem
aprovação de release.
Base histórica: branch `Atualizacao-Geral-V3`, HEAD `0a4654e` no checkpoint
de 2026-09-21; as seções posteriores registram a retomada. Data inicial:
2026-09-19.

## Verificação inicial

Antes das alterações no backend, passaram 333 testes de `tests/unit`,
`tests/integration`, `tests/contract` e `tests/load`, com `pytest -q -W error`.
A mesma seleção passou em Redis 8.0.5 temporário local e em Redis 7.4.11
na rede interna de containers. Os 18 testes de `tests/docker` também passaram
no ambiente Python local, após disponibilizar pip para a prova de wheel.
Esses números são a referência inicial, não o resultado da implementação.

O ambiente virtual local usa Python 3.12, dependências produtivas de
`requirements.lock` e dependências de build de `requirements-build.lock`.
Os extras de desenvolvimento foram instalados com restrição das versões
produtivas. Nenhum serviço ou pacote foi instalado globalmente.

O Podman forneceu `pids.max=1` a containers sem limite explícito. Isso
impediu fork/threads do Redis. O Redis de teste iniciou com limite 128;
o runner usou 256. Seccomp e isolamento de rede não foram desativados.
Os dois containers de tentativa, sem persistência, foram removidos.

Para testes nativos, um arquivo HOSTALIASES temporário mapeou `redis` para
`localhost` apenas nos processos de teste, usando porta 16379. Não houve
alteração de `/etc/hosts`, DNS ou trust store global.

## Ferramentas verificadas

Downloads oficiais conferidos por SHA-256 antes da execução:

| Ferramenta | Versão | SHA-256 do arquivo Linux amd64                                     |
| ---------- | ------ | ------------------------------------------------------------------ |
| Gitleaks   | 8.30.1 | `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| Trivy      | 0.74.0 | `2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a` |

Fontes: [Gitleaks 8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
e [Trivy 0.74.0](https://github.com/aquasecurity/trivy/releases/tag/v0.74.0).
Checkout v4.2.2 foi resolvido no repositório oficial para
`11bd71901bbe5b1630ceea73d27597364c9af683`.

## Histórico e imagem inicial

Gitleaks, com regras padrão e saída redigida, examinou 32 commits e não
encontrou segredos. A execução com as regras específicas de T16 ainda é
necessária. Isso não comprova inexistência de segredos em outros históricos,
repositórios, sistemas externos ou arquivos locais ignorados.

A imagem runtime foi construída e carregada localmente, sem publicação.
O scanner Trivy encontrou 57 ocorrências HIGH/CRITICAL na base Debian 13.6,
representando 21 CVEs diferentes, incluindo três ocorrências CRITICAL.
Há versão corrigida indicada para 13 ocorrências. O inventário Python tem
23 pacotes e não apresentou achados HIGH/CRITICAL nessa execução.

Uma comparação somente leitura com a imagem oficial Python 3.12.14,
digest `sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`,
encontrou 44 ocorrências HIGH, oito CVEs diferentes, zero CRITICAL e nenhuma
versão corrigida indicada para os achados restantes. A troca do Dockerfile
foi aplicada na retomada; o scan da imagem atual ainda precisa ser reexecutado.

Os alertas são achados do scanner, não demonstrações de exploração remota
do ClimaPrev. Por exemplo, o Debian já informa correção do
[CVE-2026-13221](https://security-tracker.debian.org/tracker/CVE-2026-13221),
mas ainda classifica a versão estável de util-linux afetada por
[CVE-2026-78408](https://security-tracker.debian.org/tracker/CVE-2026-78408).
Não foi criada exceção nem usado `ignore-unfixed` para aprovar a imagem.

## Gates pendentes no checkpoint de 2026-09-21

Ainda faltam homologação TLS/ACL, browser Playwright reproduzível, CI remoto e
verificação independente. A política de scanner foi executada e passou
localmente; o CI remoto ainda precisa confirmar o mesmo resultado no runner do
GitHub. Esta seção é histórica; a execução remota foi registrada na seção
de T19 abaixo.
DNS, firewall e certificado público de uma implantação real estão fora
das provas locais; nenhuma prontidão de produção foi declarada.

## Ponto de parada e resultados parciais

A última regressão do ponto de parada teve **419 testes aprovados e 14
falhas**, totalizando 433. Após restaurar o `flushdb` original da fixture de
`test_end_to_end.py`, a retomada confirmou **437 testes aprovados** em Redis
descartável; nenhuma limpeza foi feita em Redis compartilhado.

Passaram separadamente 17 testes de política de arquivos e provisionamento:

```bash
pytest -q -W error tests/docker/check_secret_file_policy.py tests/docker/check_secret_provision.py
```

Ruff passou com `--ignore EXE002`; mypy passou em 41 arquivos de origem.
`git diff --check` e os validadores estritos de spec/tasks passaram. Esses
resultados não substituem a regressão completa ou os demais gates.

Uma prova exploratória com Playwright 1.63.0/Firefox 155.0 confirmou que
HTTPS falha sem a CA local e funciona após importá-la em perfil temporário.
Não houve `ignoreHTTPS`, alteração do trust store global ou aceitação
completa do frontend. O contrato estático/HTTP de T15 foi criado na retomada;
o teste Playwright reproduzível com CA explícita ainda precisa ser executado.

O agente auxiliar foi encerrado antes de entregar sua conclusão. Os dois
containers temporários ainda ativos e o Redis nativo de teste foram parados.
Nenhum serviço foi publicado, nem segredos reais foram rotacionados.

Os relatórios brutos do scanner e a prova exploratória estavam em `/tmp`.
Em 2026-09-21, o diretório de ferramentas/relatórios não estava mais presente.
Os números acima são o registro das saídas observadas, não relatórios brutos
versionados; reproduzir scans para o aceite final. Veja o
[contexto](context.md) para os limites do snapshot e a ordem de retomada.

## Verificações do checkpoint — 2026-09-21

O checkpoint seleciona 41 arquivos de segurança e contexto, deixando 34
arquivos com alterações anteriores fora do staging. Não inclui `.env` real,
`.homolog`, `.specs`, arquivos privados do SIGFAS ou relatórios com segredos.

Foram reexecutados, sem iniciar serviços nem retomar implementação:

- Os dois gates de host de arquivos/provisionamento: **17 passed**.
- Ruff com `--ignore EXE002`: aprovado.
- Mypy: aprovado nos 41 arquivos de origem.
- Validadores estritos de spec/tasks: zero erros e zero avisos.
- `git diff --check` e `git diff --cached --check`: aprovados.
- Verificação de 52 referências internas dos documentos de contexto e
  planejamento: nenhum destino ausente. As 31 referências locais ao SIGFAS
  permanecem evidências da máquina original, não arquivos deste repositório.

O Gitleaks 8.30.1 foi baixado novamente da distribuição oficial, com o mesmo
SHA-256 verificado acima. A cópia exata do índice Git, exportada em diretório
temporário, apresentou um achado `generic-api-key` em `.env.example`, linha 18:
a variável `CLIMAPREV_PROVIDER_ALLOWED_HOSTS` contém somente os três domínios
públicos dos provedores, sem credencial. A inspeção classificou esse achado
como falso positivo. O scanner retornou finding; não foi apresentado como
sucesso sem ressalvas nem foi criada supressão para ocultá-lo. T16 deve cobrir
esse exemplo público com teste negativo e tratamento estritamente específico,
sem liberar todos os exemplos, documentos ou testes.

Essas verificações servem para registrar o checkpoint, não para aprovar uma
release. A regressão completa, imagem atualizada, homologação e revisão
independente continuam pendentes conforme o contexto.

## Retomada local — 2026-09-21

Executada após o pedido de continuidade, com a stack local e Redis descartável:

| Gate | Resultado |
| --- | --- |
| Suíte completa `pytest -q -W error` | **437 passed** |
| `docker compose config --quiet` | **passou** |
| `docker compose --profile load config --quiet` | **passou** |
| Build `app` e runtime | **passou** |
| Ruff com `--ignore EXE002` | **passou** |
| Mypy em `src` | **passou em 41 arquivos** |
| `nginx -t` no frontend | **passou** |
| Local body/método/rota | 413 para body >16 KiB, 403 para PUT, 404 para rota desconhecida |
| Frontend/security HTTP smoke | **passou** |
| Load smoke | 3 requisições, 0 falhas; Redis e redes próprios/internal |
| Rotação sintética | **passou**, sem exibir valores |

Alterações aplicadas neste lote: rotas Nginx exatas e negação padrão, headers
em erro, limite de body, access log bruto desativado no local, busca no
coletor, Redis/rede exclusivos do perfil load, `app-load` em allowed hosts,
`--no-access-log`, HMAC montado somente no app de homologação, base Python
atualizada, contrato estático/HTTP do frontend, `.gitleaks.toml`, workflow de
segurança e runbook de rotação.

Não foram executados: Gitleaks/Trivy nesta sessão, homologação TLS/ACL com os
secrets do engine Windows, Playwright completo com CA explícita, execução
remota do workflow e revisão independente. O workflow está preparado para
bloquear findings HIGH/CRITICAL e não usa `ignore-unfixed`; a ausência dessas
execuções impede declarar produção pronta.

## Validação de navegador — 2026-09-23

Foi feita uma validação interativa no navegador contra a stack local em
`http://127.0.0.1:8080/`, usando somente dados sintéticos e uma localidade
pública. Foram observados:

- carregamento do documento com título e estrutura acessível;
- `styles.css` e `app.js` carregados pela mesma origem;
- submissão vazia rejeitada pela validação nativa, sem chamada de consulta;
- consulta sintética de `Sao Paulo` concluída e resultado renderizado como
  texto, incluindo risco, período, fonte e alerta de dados indisponíveis;
- nenhum erro ou aviso de console capturado durante a jornada;
- nenhum segredo, URL de provedor ou conteúdo HTML interpretável exposto no
  DOM público.

Essa execução fecha a evidência manual do fluxo local de T15, mas não fecha o
gate obrigatório de HTTPS/homologação. Depois dela, o runner Playwright
versionado com CA explícita foi criado e integrado ao CI; a execução real do
runner ainda depende de um ambiente em que o navegador possa iniciar. A
validação local executada foi:

```text
Frontend security acceptance contract: OK.
Local frontend proxy identity configuration: OK.
Synthetic secret rotation contract: OK.
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

## Execução autorizada de T16/T17 — 2026-09-23

Com autorização explícita, os scanners foram executados em containers pinados:

- Gitleaks 8.30.1, digest
  `sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f`:
  **passou**, examinando 33 commits e aproximadamente 1,92 MB, sem leaks.
- A imagem `climaprev-security-runtime:ci` foi reconstruída com a base Alpine
  fixada no digest Python versionado e `apk upgrade --no-cache`.
- Trivy 0.74.0, digest
  `sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969`:
  **passou**, com 0 vulnerabilidades HIGH/CRITICAL na imagem Alpine final.
  Os pacotes Python também não apresentaram achados HIGH/CRITICAL.

O código de saída do Trivy foi 0, com `ignore-unfixed` desativado. Nenhuma
exceção foi criada. Naquele checkpoint, T16 estava verificado e T17 aprovado
localmente; o workflow remoto passou posteriormente, conforme a seção de
T19.

A regressão final da aplicação executada no container `app` passou com
**437 testes**, em 39,24 s, já com a base Alpine atualizada. Ruff, mypy,
Nginx, contratos de frontend/proxy, Compose e rotação sintética também
passaram. Naquele checkpoint, o CI remoto ainda precisava reproduzir esses
gates; a execução posterior está registrada na seção de T19.

## Runner de navegador — 2026-09-23

Foi criado `tests/docker/check_frontend_browser.py` com Playwright `1.63.0`
instalado somente no runner de teste/CI, sem dependência produtiva na imagem
Alpine. O fluxo HTTP valida título, CSS, submissão por coordenadas e renderiza
um payload sintético contendo markup; confirma que o texto permanece no DOM sem
criar `img`, `script` ou atributo de evento. O fluxo HTTPS exige `--ca-file` e
importa a CA em perfil Firefox temporário, sem `ignore_https_errors` e sem
alterar o trust store global.

O lint, o type check da origem e a compilação sintática do runner passaram. A
execução interativa local ficou bloqueada pelo ambiente Windows: o instalador
baixou o Chrome, mas o shell headless esperado não foi disponibilizado e o
processo do navegador retornou `spawn UNKNOWN`; a tentativa de baixar o
FFmpeg adicional também encontrou falha de DNS. Portanto, T15 foi avançada
com implementação e workflow, mas a aceitação Browser/Homolog completa ainda
não deve ser marcada como concluída.

## Retomada T14–T18 — 2026-09-23

Os parágrafos anteriores descrevem o histórico do checkpoint, não o estado
atual. Todas as provas desta seção usaram credenciais e certificados
sintéticos, sem alterar os recursos produtivos nem expor valores.

| Tarefa | Resultado local | Limite |
| --- | --- | --- |
| T14 | Compose homolog com Redis e Nginx pinados por digest, UID fixo sem root, rootfs somente leitura, capabilities removidas, secrets por consumidor; topologia, ACL/readiness, TLS/CA, logs sanitizados e reinício do coletor passaram | Stack sintética, não ambiente produtivo |
| T15 | Runner Playwright 1.63.0 pinado passou em HTTP local e HTTPS homolog; CSS, mesma origem, DOM inerte, storage vazio e CA explícita | Não é auditoria formal de acessibilidade |
| T16 | Gitleaks com regras padrão examinou 34 commits após o commit de segurança; fixture bloqueou tokens sintéticos em `.env.example` e em outro arquivo, com saída redigida | Uma exceção histórica por fingerprint exato em `.gitleaksignore` |
| T17 | Gitleaks, Trivy, Browser, Homolog e regressão passaram localmente e no GitHub Actions | Não substitui revisão independente nem controles de produção |
| T18 | Runbook e rotação de dois conjuntos sintéticos; senha anterior recusada, nova aceita e duas execuções compartilharam a mesma cota Redis/HMAC | Não houve rotação real nem validação de DNS/firewall/certificado público |

O Redis efêmero recriado inicia com cache/cota frios. A nova chave HMAC
separa identidades da geração anterior; esse efeito foi registrado no
runbook, sem afirmar preservação da cota durante a rotação.

**Correção importante de T16:** a primeira versão local de
`.gitleaks.toml` não herdava as regras padrão; portanto o passe inicial
de Gitleaks anotado acima não demonstrava detecção efetiva. A configuração
final ativa explicitamente `useDefault = true`. A linha de hosts públicos
em `.env.example` gerou um único falso positivo no commit
`7ac70d82d2eb9d424244eb36a70ae5a9f055c843`; a exceção ignora só o
fingerprint desse achado. Com a configuração final, a fixture positiva
retornou finding, a negativa passou e a varredura dos 33 commits terminou
sem achados não exceptuados. Falha do scanner também resulta em código
não zero no gate.

O Trivy 0.74.0 examinou a imagem runtime Alpine final, detectou pacotes do
sistema e Python e retornou código 0 com **zero HIGH/CRITICAL**;
`ignore-unfixed` permaneceu desativado. O CI repetiu o gate com sucesso;
o resultado é específico da base de vulnerabilidades consultada em
2026-09-23 e não garante ausência futura de achados.

Após rebuild da imagem de desenvolvimento, `pytest -q -W error` passou com
**437 testes**; Ruff passou com `--ignore EXE002` e mypy passou nos
**41 arquivos** de origem. `git diff --check` não encontrou erros.
`docker compose -f docker-compose.homolog.yml config --quiet` passou com
variáveis sintéticas em processo; sem essas variáveis, o Compose corretamente
recusa a configuração. A stack final foi recriada com os digests pinados
antes dos smokes de topologia, hardening, frontend, TLS e Redis.
O workflow de segurança também passou no `actionlint 1.7.12` em container
oficial. A stack sintética e seus volumes foram encerrados, e os diretórios
temporários de certificados/segredos sintéticos foram removidos; a stack
local de desenvolvimento permaneceu intacta.

## Gates remotos — 2026-09-23

Commit `525854ab132e4db37bde9b483468e72ac36cdf10` foi enviado à
branch `Atualizacao-Geral-V3` após nova varredura Gitleaks dos 34 commits.
O [CI](https://github.com/0SunnyBoy/climaprev/actions/runs/35878967535)
e o [Security gates](https://github.com/0SunnyBoy/climaprev/actions/runs/35878967681)
terminaram com conclusão **success**. No workflow de segurança, passaram
política de arquivos, fixture e histórico Gitleaks, build runtime,
Playwright local, homologação TLS/Browser, rotação sintética, Trivy,
regressão e limpeza final. Ambos usaram o runner Ubuntu do GitHub; nenhum
segredo produtivo foi fornecido a esses jobs.

## T19 — decisão consolidada — 2026-09-23

Foi feita uma segunda passagem da matriz de requisitos, dos artefatos
versionados e dos gates locais/remotos. O conjunto avaliado corresponde ao
commit de segurança `525854a` e ao registro documental `83dd264`; as mudanças
locais não commitadas em `risk_evaluator.py` e no teste correspondente foram
deliberadamente excluídas.

| Evidência | Resultado |
| --- | --- |
| Regressão atual no container | `437 passed` com `pytest -q -W error` |
| Qualidade estática | Ruff aprovado com `--ignore EXE002`; mypy aprovado em 41 arquivos |
| Compose | Configuração local e perfil `load` aprovados com `config --quiet` |
| Segredos/histórico | Gitleaks com regras padrão, fixture positiva/negativa e 34 commits aprovados |
| Imagem | Trivy sem vulnerabilidades HIGH/CRITICAL, sem `ignore-unfixed` |
| Fronteira web | Browser HTTP local e HTTPS de homologação com CA explícita aprovados |
| Homologação | Topologia, ACL Redis, TLS, hardening, logs e rotação sintética aprovados |
| CI remoto | Workflows `CI` e `Security gates` concluídos com `success` no GitHub |

Todos os requisitos têm evidência controlada; `NET-01`, `IP-01` e `OPS-01`
continuam condicionados à validação operacional real. A revisão de T19
encontrou estes bloqueios de publicação:

1. DNS, firewall, certificado público, ingress e NAT do ambiente real não
   foram verificados.
2. Secrets reais, permissões do host, armazenamento e procedimento de
   observabilidade do ambiente de produção não foram exercitados.
3. Falta uma aprovação independente do proprietário/operador após revisar
   esta matriz.
4. A imagem e a base de vulnerabilidades precisam ser escaneadas novamente
   no momento da publicação, pois o resultado do Trivy é temporal.

**Decisão T19:** ciclo de segurança T1–T19 **concluído com decisão
condicional**. Os controles implementados estão verificados nos ambientes
controlados e no CI remoto, mas a aplicação está **não pronta para produção**
até que os quatro bloqueios acima sejam resolvidos e registrados. Esta
decisão não autoriza deploy, rotação real ou alteração de branch protection.
