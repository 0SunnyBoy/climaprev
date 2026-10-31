# Segredos e operação segura

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Este guia descreve somente o ciclo local/homologação com valores sintéticos.
Ele não autoriza publicar a aplicação, rotacionar credenciais reais ou alterar
branch protection.

## Inventário sem valores

| Segredo | Consumidor | Montagem | Não deve aparecer em |
| --- | --- | --- | --- |
| `redis.password` | `app` | `/run/secrets/redis_password` | frontend, collector, Nginx, Git, logs |
| `client-ip-hmac.key` | `app` | `/run/secrets/client_ip_hmac_key` | frontend, collector, Git, logs |
| `redis.acl` | Redis | `/run/secrets/redis_acl` | app, frontend, collector, Git |
| `server.crt`/`server.key` | entrada TLS | `/run/secrets/tls_*` | app, frontend assets, Git, logs |

`.env` organiza configuração; não cifra valores. O administrador do host e o
engine de containers continuam sendo fronteiras de confiança.
O IP visto pelo rate limiter depende do proxy e de eventual NAT anterior;
o guia local não garante identificar o IP público original em toda topologia.

## Provisionamento sintético

Siga o [guia de homologação](homologacao.md) para gerar um conjunto novo, TLS
de teste e iniciar a stack. O provisionador recusa um diretório já existente e
não imprime valores. Confira o Compose com `config --quiet` antes de iniciar.

A stack de homologação usa usuários fixos sem root, sistema de arquivos base
somente leitura, nenhuma capability Linux adicional e volumes temporários para
arquivos de execução. O [smoke de hardening](../../tests/docker/check_homolog_hardening.py)
confere usuários, montagens e leitura de cada secret no contêiner real.

## Rotação ensaiada

Em uma stack **exclusivamente sintética**, com `.homolog` inicial já criado:

```bash
python docker/homolog/provision.py .homolog/next --capacity 60 --refill 60 --window 60
python docker/homolog/entrada/provision_tls.py .homolog/next
docker compose --env-file .homolog/next/compose.env -f docker-compose.homolog.yml config --quiet
docker compose --env-file .homolog/next/compose.env -f docker-compose.homolog.yml up -d --force-recreate
python tests/docker/check_secret_rotation_runtime.py --old-password-file .homolog/redis.password
python tests/docker/check_homolog_hardening.py
python tests/docker/check_homolog_frontend.py --ca-file .homolog/next/ca.crt --env-file .homolog/next/compose.env
```

O ensaio rejeita a senha antiga e faz duas execuções independentes usarem a
mesma cota HMAC no Redis. O [smoke Redis](../../tests/docker/check_homolog_redis.py)
confirma a senha nova, cache sintético, lock e comandos proibidos. Preserve o
diretório anterior durante a verificação. Em uma operação real, prepare a
troca em ambiente isolado e coordene a revogação antes de direcionar tráfego.
Como o Redis de homologação é efêmero, recriá-lo deixa cache e cotas frios;
trocar a chave HMAC também muda o namespace de identidade. Planeje esse
reinício de cota antes de aplicar rotação com tráfego real.

Se a validação falhar, interrompa a troca e preserve as evidências sem valores.
Retorne à versão conhecida da aplicação mantendo credenciais válidas; uma
credencial suspeita ou revogada não deve ser reutilizada. Descarte conjuntos
sintéticos após encerrar os contêineres de teste.

Rollback é voltar ao artefato de aplicação conhecido, não reutilizar segredo
antigo comprometido. Em produção, o proprietário deve coordenar revogação,
substituição e reinício dos workers.

## Diagnóstico permitido

Use `docker compose config --quiet`, status de saúde, códigos HTTP e IDs de
requisição. Não cole `compose config` expandido, `env`, conteúdo de secrets,
URLs completas de provedor ou logs brutos em issues/artefatos.

## Status

Os gates locais de homologação/TLS e o ensaio de rotação passaram com dois
conjuntos sintéticos em 2026-09-23; o workflow remoto também passou. A
revisão independente e os controles de rede/certificado do ambiente real não foram
validados; nenhuma prontidão de produção é declarada.
