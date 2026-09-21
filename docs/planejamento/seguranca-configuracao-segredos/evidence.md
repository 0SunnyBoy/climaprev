# Evidências de execução da segurança

Estado: pausado; checkpoint solicitado em 2026-09-21, sem aprovação de release.
Base: branch `Atualizacao-Geral-V3`, HEAD `0a4654e`, com mudanças locais
anteriores preservadas. Data inicial: 2026-09-19.

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
foi apresentada ao usuário e ainda não foi realizada nesta etapa.

Os alertas são achados do scanner, não demonstrações de exploração remota
do ClimaPrev. Por exemplo, o Debian já informa correção do
[CVE-2026-13221](https://security-tracker.debian.org/tracker/CVE-2026-13221),
mas ainda classifica a versão estável de util-linux afetada por
[CVE-2026-78408](https://security-tracker.debian.org/tracker/CVE-2026-78408).
Não foi criada exceção nem usado `ignore-unfixed` para aprovar a imagem.

## Gates pendentes

Ainda faltam a regressão após as alterações, smokes de entrada/TLS/ACL,
browser, isolamento de carga, política de scanner, ensaio de rotação e
verificação independente. O gate de vulnerabilidades está bloqueado pelos
achados acima até correção ou decisão de risco explícita do responsável.
DNS, firewall e certificado público de uma implantação real estão fora
das provas locais; nenhuma prontidão de produção foi declarada.

## Ponto de parada e resultados parciais

A última regressão completa recebida após as alterações teve **419 testes
aprovados e 14 falhas**, totalizando 433. As falhas eram de isolamento de
cache: 12 em `test_evolution_data.py` e duas em
`test_provider_failure_contract.py`. O `flushdb` original da fixture de
`test_end_to_end.py` foi restaurado antes da interrupção, exclusivamente
para Redis descartável de teste. Não foi recebido resultado completo depois
desse ajuste; a correção ainda precisa ser comprovada por nova execução.

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
completa do frontend. O teste reproduzível de T15 ainda precisa ser criado.

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
