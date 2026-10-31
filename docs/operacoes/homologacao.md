# Homologação local

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.
>
> Gate HTTPS local entre origens distintas aprovado com API real e upstream sintético. TLS CA/hostname verificados separadamente; navegador com pin SPKI restrito ao processo. Isso não é homologação do INMET ao vivo ou de DNS/TLS públicos. Campanha local limitada: 3.000 requisições sem falhas; hospedagem adiada.

## Situação vigente — 20/10/2026

O procedimento foi executado na stack isolada, inclusive TLS, Redis, hardening,
logs e rotação sintética. Consulte [validação local](validacao-local-2026-10-19.md)
para resultados, adaptação Windows/OpenSSL e limites. O diretório `.homolog/`
existe localmente e permanece ignorado pelo Git; as credenciais mais recentes
estão em `.homolog/next/`. As falhas anteriores de download do runner permanecem no registro histórico. Depois, o gate HTTPS local entre origens distintas passou com Edge 155, API real e upstream sintético; reprodução em [gate independente](../../tests/docker/decoupling/README.md). Isso não comprova execução do runner Python fixado nem de todos os gates do workflow Security. Leitor de tela manual, INMET real e homologação de hospedagem continuam pendentes.

## Procedimento e registro anterior

O procedimento abaixo descreve a stack isolada e pode ser reproduzido na máquina de homologação. `.homolog/` foi provisionado localmente, mas não é versionado. Não repetir o provisionamento sobre arquivos existentes nem incluir chaves/credenciais no Git; seguir as recusas de sobrescrita e a sequência de rotação.

A stack `climaprev-homolog` é separada do desenvolvimento. API e Redis não
publicam portas. Redis exige ACL, limita chaves ao prefixo versionado
`climaprev:production:` e
fica em rede interna; somente o app participa dessa rede. O app dispõe de
rede separada para saída aos provedores HTTPS permitidos.

Provisionar uma única vez, escolhendo explicitamente a cota local. Os valores
abaixo são uma fixture de homologação, não um orçamento contratado do provedor.

```bash
python3 docker/homolog/provision.py .homolog --capacity 60 --refill 60 --window 60
python3 docker/homolog/entrada/provision_tls.py .homolog
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml config --quiet
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml build
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml up -d
```

O diretório gerado tem modo 0700 e é ignorado pelo Git/contexto de build.
Ele contém senha Redis, chave HMAC independente, ACL e material TLS. A senha
e a chave HMAC são montadas somente no app; ACL vai somente ao Redis e TLS vai
somente à entrada. `CLIMAPREV_ALLOWED_HOSTS` deve ser explícito para o domínio
da entrada (o default local é `localhost`).
Arquivos de secret têm modo 0444 e são montados somente nos respectivos
serviços, como leitura. Compose sobre Podman ignora uid/gid/mode de file
secrets; o funcionamento não depende desses campos. Não alterar permissões
de segredos externos preexistentes. O provisionador recusa sobrescrever um
diretório existente. Senha não aparece em argumentos, variáveis de ambiente
ou relatórios. Apenas o caminho do arquivo entra na configuração.

O healthcheck Redis confirma que o servidor exige autenticação; a readiness
da API faz PING autenticado. O cache não possui persistência AOF/snapshot.
A comprovação explícita pode ser executada com o script montado:

```bash
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml exec -T app python < tests/docker/check_homolog_redis.py
```

Para parar apenas esta stack: `docker compose --env-file .homolog/compose.env
-f docker-compose.homolog.yml down`. Não remover a stack de desenvolvimento
ou recursos de outros projetos. A entrada TLS fica em `https://localhost:18443`.


## TLS e fronteira de proxy

A CA de teste vale 30 dias. Somente `server.crt` e `server.key` são montados
na entrada; a chave privada da CA fica no diretório local. Nenhum trust store
global é alterado. Verificar com CA explícita:

```bash
curl --cacert .homolog/ca.crt https://localhost:18443/health/live
python3 tests/docker/check_homolog_tls.py
python3 tests/docker/check_homolog_frontend.py
```

Um navegador de homologação deve confiar nessa CA em perfil isolado. Não
usar ignoreHTTPS, certificados ignorados ou desabilitar validação TLS.
Para a aceitação automatizada, construa a imagem de teste pinada e execute o
runner com a CA explícita. No PowerShell:

```powershell
docker build -f tests/docker/Playwright.Dockerfile -t climaprev-playwright-test:local tests/docker
docker run --rm --network container:climaprev-homolog-entrada-1 `
  --mount "type=bind,source=$((Resolve-Path tests/docker).Path),target=/work/tests/docker,readonly" `
  --mount "type=bind,source=$((Resolve-Path .homolog/ca.crt).Path),target=/test-ca.crt,readonly" `
  -w /work climaprev-playwright-test:local python tests/docker/check_frontend_browser.py `
  --base-url https://localhost:8443 --ca-file /test-ca.crt
```

O runner importa a CA em um perfil Firefox temporário, valida CSS e JavaScript
na mesma origem, storage vazio e texto sintético inerte no DOM. O perfil é
descartado ao fim; nenhum trust store global é alterado. A imagem de teste usa
Playwright 1.63.0 e base fixada por digest em
`tests/docker/Playwright.Dockerfile`.
`/internal` e `/internal/*`, inclusive caminhos codificados/normalizados,
retornam 404 pela entrada. A rota interna continua disponível ao operador por
`docker compose exec app`, sem porta publicada da API.

Nginx sobrescreve X-Forwarded-For e tem IP fixo na rede `ingress`, único IP
confiável no app. `CLIMAPREV_INGRESS_SUBNET`, `CLIMAPREV_PROXY_IP` e `CLIMAPREV_APP_IP` precisam
ser ajustados juntos se houver conflito de subnet; o valor padrão é
`10.253.248.0/24`, com proxy `10.253.248.2` e app `10.253.248.3`. Uvicorn mantém proxy headers
próprios desabilitados. A publicação é somente loopback, porta 18443, alterável
por `CLIMAPREV_HOMOLOG_PORT`.

**Limitação local observada:** Podman rootless reescreve a origem da conexão
do host. O limite individual usa o endereço efetivamente percebido pelo proxy;
esta stack não promete preservar os IPs originais de usuários externos.

## Coleta e retenção de logs

App e Nginx enviam somente eventos JSON por socket Unix privado. O coletor
não possui rede; somente ele monta o volume persistente `sanitized-logs`.
A entrada do socket aceita até 8192 bytes e guarda exclusivamente evento,
request ID validado, rota de conjunto fixo, status, duração e horário local
de registro. Campos extras são descartados; caminhos desconhecidos viram
`unmatched`. Erros inesperados 500 também geram metadados e envelope sanitizado,
sem traceback bruto ou body do provedor. Cancelamento continua propagado.

Cada arquivo agrupa uma hora e tem limite de 1 MiB, mantendo os registros
completos mais recentes se o limite for atingido. Há até 168 arquivos, cerca de
168 MiB. Sete dias é um **teto**, não uma garantia de armazenamento mínimo:
a limpeza começa 60 s antes de completar sete dias desde o início da hora do
arquivo e roda a cada 60 s, inclusive sem tráfego. Essa precisão pode remover
um registro até cerca de uma hora antes. A inicialização remove expirados
antes de receber novos eventos. Enquanto a máquina/coletor estiver parado,
a remoção física depende da próxima inicialização; o teste cobre essa retomada.

A coleta é operacional, não uma trilha de auditoria durável. O socket pode
perder eventos durante indisponibilidade/saturação; o teste confirma reconexão
após reinício. Os quatro serviços desta stack usam logging driver `none`
para não manter cópias sem retenção no engine. `docker compose logs` não é a
fonte de diagnóstico desse perfil. Para ler os arquivos sanitizados:

```bash
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml exec collector python -c "from pathlib import Path; print(''.join(p.read_text() for p in sorted(Path('/var/log/climaprev').glob('*.jsonl'))))"
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml ps
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml exec entrada nginx -t
```

Executar provas no app com `exec`: um `compose run app` herdaria o IP fixo
e conflitaria com o serviço ativo.

O healthcheck app executa um módulo Python: evita a divisão de argumentos de
`python -c` observada na API de healthcheck do Podman. Os testes de retenção
usam relógio controlado e timeout real de socket, sem esperar sete dias.
