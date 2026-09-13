# Homologação local

A stack `climaprev-homolog` é separada do desenvolvimento. API e Redis não
publicam portas. Redis exige ACL, limita chaves ao prefixo `climaprev:` e
fica em rede interna; somente o app participa dessa rede. O app dispõe de
rede separada para saída aos provedores HTTPS permitidos.

Provisionar uma única vez, escolhendo explicitamente a cota local. Os valores
abaixo são uma fixture de homologação, não um orçamento contratado do provedor.

```bash
python3 docker/homolog/provision.py .homolog --capacity 60 --refill 60 --window 60
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml config --quiet
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml build
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml up -d
```

O diretório gerado tem modo0700 e é ignorado pelo Git/contexto de build.
Arquivos de secret têm modo0444 e são montados somente nos respectivos
serviços, como leitura. Compose sobre Podman ignora uid/gid/mode de file
secrets; o funcionamento não depende desses campos. Não alterar permissões
de segredos externos preexistentes. O provisionador recusa sobrescrever um
diretório existente. Senha não aparece em argumentos, variáveis de ambiente
ou relatórios. Apenas o caminho do arquivo entra na configuração.

O healthcheck Redis confirma que o servidor exige autenticação; a readiness
da API faz PING autenticado. O cache não possui persistência AOF/snapshot.
A comprovação explícita pode ser executada com o script montado:

```bash
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml run --rm --no-deps -v "$PWD/tests/docker/check_homolog_redis.py:/check.py:ro" app python /check.py
```

Para parar apenas esta stack: `docker compose --env-file .homolog/compose.env
-f docker-compose.homolog.yml down`. Não remover a stack de desenvolvimento
ou recursos de outros projetos. A entrada TLS será acrescentada em T20.
