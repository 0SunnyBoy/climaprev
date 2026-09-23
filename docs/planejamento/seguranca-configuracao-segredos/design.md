# Design — segurança orientada por evidência

Estado: desenho implementado/validado até T18 com dados sintéticos;
revisão independente e T19 pendentes.
Data: 2026-09-19.

Atualização de 2026-09-23: gates locais e workflows remotos passaram para
`525854a`. Consulte o [contexto](context.md) para separar essas provas
da validação ainda necessária no ambiente real.

[Spec](../../../docs/planejamento/seguranca-configuracao-segredos/spec.md) ·
[Tasks](../../../docs/planejamento/seguranca-configuracao-segredos/tasks.md).

## Escopo e método da análise

Inspeção estática das cópias locais: código, configuração, metadados Git,
Docker, fluxos de autenticação, proxy, Redis, logs, frontend e testes.
As árvores têm alterações locais: os hashes identificam a base, não um
snapshot completo do conteúdo inspecionado.

| Projeto         | Cópia analisada                                                  | Base HEAD                                |
| --------------- | ---------------------------------------------------------------- | ---------------------------------------- |
| ClimaPrev       | `/home/ney/Documentos/clima prev/climaprev-Atualizacao-Geral-V3` | `0a4654e`, branch `Atualizacao-Geral-V3` |
| SIGFAS backend  | `/home/ney/Documentos/fullstack/sigfas-server`                   | `3777f23b`                               |
| SIGFAS frontend | `/home/ney/Documentos/fullstack/sigfas-social`                   | `a778e8b`                                |

Não foram lidos os valores dos `.env` reais, testadas credenciais, acessados
bancos de produção, executados ataques ou auditados todos os módulos de
negócio. A existência de uma configuração no código não prova exposição na
internet. Não houve auditoria completa de histórico, CVEs, IAM, firewall,
backups, DNS ou configuração do servidor Keycloak. Esses limites impedem
afirmar que foram descobertas todas as vulnerabilidades dos sistemas.

Prioridades deste documento: P0 = tratar imediatamente pelo proprietário se
o segredo estiver válido; P1 = resolver antes de exposição pública;
P2 = reforço e prevenção. São prioridades de triagem, não pontuações CVSS.

## O que o SIGFAS realmente protege

| Controle observado                                   | Evidência                                                                                                                                                                          | O que aproveitar no ClimaPrev                                                                                                                                       |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Senha de usuário com bcrypt e salt aleatório         | [Repositório de usuários](/home/ney/Documentos/fullstack/sigfas-server/src/users/users.repository.ts:69)                                                                           | Distinguir senha de usuário, que é verificada por hash, de credencial de serviço, que precisa ser fornecida ao serviço. ClimaPrev não possui usuários neste escopo. |
| Verificação de assinatura e expiração JWT            | [Estratégia JWT](/home/ney/Documentos/fullstack/sigfas-server/src/auth/jwt.strategy.ts:10)                                                                                         | Autorizar no servidor, não pela aparência da interface. Não adicionar JWT sem uma funcionalidade privada.                                                           |
| Verificação de titular/admin em troca de senha       | [Controller de autenticação](/home/ney/Documentos/fullstack/sigfas-server/src/auth/auth.controller.ts:73)                                                                          | Separar superfície operacional da API pública. A existência de um guard não comprova autorização de todos os endpoints.                                             |
| Backend usa variáveis para conexão principal         | [Módulo principal](/home/ney/Documentos/fullstack/sigfas-server/src/app.module.ts:408)                                                                                             | Configuração externa tipada e validada, sem defaults secretos.                                                                                                      |
| Frontend diferencia chamada SSR e navegador          | [Cliente HTTP](/home/ney/Documentos/fullstack/sigfas-social/src/utils/http.ts:5)                                                                                                   | Preservar frontend sem segredos e backend responsável por integrações internas.                                                                                     |
| Token de recuperação aleatório e invalidado na troca | [Geração](/home/ney/Documentos/fullstack/sigfas-server/src/auth/auth.service.ts:81) e [invalidação](/home/ney/Documentos/fullstack/sigfas-server/src/users/users.repository.ts:94) | Aleatoriedade e ciclo de vida explícito; não copiar esse fluxo de contas para ClimaPrev.                                                                            |

## Achados do SIGFAS que não devem ser copiados

| ID / prioridade      | Evidência estática e limite da conclusão                                                                                                                                                                                                                                                                                                                                                        | Risco / encaminhamento                                                                                                                                                                                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S01 / P0 condicional | [JWT module](/home/ney/Documentos/fullstack/sigfas-server/src/auth/auth.module.ts:14) e [mailer](/home/ney/Documentos/fullstack/sigfas-server/src/configs/mailer.config.ts:15) possuem segredos literais; os arquivos estão rastreados. AuthModule e mailer são importados no app.                                                                                                              | Tratar como potencial exposição; proprietário avalia e rotaciona os valores válidos. Não foi provado que a chave de assinatura desse módulo seja aceita pela estratégia de verificação com chave pública.                                                                                                                       |
| S02 / P0 condicional | [Configuração iron-session](/home/ney/Documentos/fullstack/sigfas-social/src/utils/iron-config.ts:1) contém senha literal e `secure: false`; [login API](/home/ney/Documentos/fullstack/sigfas-social/src/pages/api/login.ts:20) usa sessão.                                                                                                                                                    | A proteção da sessão depende de segredo exclusivo e cookie restrito a HTTPS no ambiente real. Não assumir proteção só por usar biblioteca de sessão.                                                                                                                                                                            |
| S03 / P1             | `.env` do frontend aparece em `git ls-files`; [regras de exclusão](/home/ney/Documentos/fullstack/sigfas-social/.gitignore:27) estão comentadas. Conteúdo real não foi inspecionado. Backend também não possui regra `.env` no [gitignore](/home/ney/Documentos/fullstack/sigfas-server/.gitignore).                                                                                            | Rastrear `.env` é risco confirmado de configuração; presença de credenciais válidas nesse arquivo não foi confirmada. Ignorar depois não apaga commits antigos.                                                                                                                                                                 |
| S04 / P1             | [Validação frontend](/home/ney/Documentos/fullstack/sigfas-social/src/utils/auth.ts:34) registra token ao capturar erro. [Interceptor backend](/home/ney/Documentos/fullstack/sigfas-server/src/interceptors/logger.interceptor.ts:19) exclui dois campos de senha, mas registra outros dados de body, query, params, IP e usuário; é registrado globalmente.                                   | Redação por lista de campos proibidos é insuficiente. Adotar lista positiva de metadados; investigar retenção/acesso aos logs existentes em trabalho separado.                                                                                                                                                                  |
| S05 / P1             | [TypeORM ativo](/home/ney/Documentos/fullstack/sigfas-server/src/app.module.ts:414) usa `rejectUnauthorized: false` fora de teste e `synchronize: true`.                                                                                                                                                                                                                                        | TLS sem validação de servidor enfraquece autenticidade; sincronização automática amplia risco de alteração de schema. Não copiar. O [arquivo estático antigo](/home/ney/Documentos/fullstack/sigfas-server/src/configs/typeorm.config.ts:3) também tem literal sensível, mas seu uso direto está comentado no módulo principal. |
| S06 / P1             | [Recuperação](/home/ney/Documentos/fullstack/sigfas-server/src/auth/auth.service.ts:75) diferencia usuário inexistente; token é armazenado diretamente, e [reset](/home/ney/Documentos/fullstack/sigfas-server/src/auth/auth.service.ts:108) não verifica prazo. [Entidade](/home/ney/Documentos/fullstack/sigfas-server/src/users/entities/user.entity.ts:37) não contém expiração específica. | Enumerar contas e aceitar token antigo são riscos do fluxo inspecionado. O token é invalidado após troca; não afirmar reutilização posterior. Futuro fluxo exigiria TTL, armazenamento por hash e resposta uniforme.                                                                                                            |
| S07 / P1             | [Controller mobile](/home/ney/Documentos/fullstack/sigfas-server/src/mobile-auth/mobile-auth.controller.ts:9) chama [login por CPF/e-mail](/home/ney/Documentos/fullstack/sigfas-server/src/mobile-auth/mobile-auth.service.ts:18), retornando dados pessoais sem desafio de posse no fluxo observado.                                                                                          | CPF/e-mail não são segredos autenticadores. Exposição efetiva depende da implantação e de proteções externas não verificadas. Não copiar essa autenticação.                                                                                                                                                                     |
| S08 / P1, hipótese   | [TenantService](/home/ney/Documentos/fullstack/sigfas-server/src/tenant/tenant/tenant.service.ts:6) mantém tenant em atributo mutável do serviço, alimentado pelo [guard](/home/ney/Documentos/fullstack/sigfas-server/src/tenant/tenant.guard.ts:9).                                                                                                                                           | Investigar escopo de injeção e concorrência antes de concluir vazamento entre tenants. Não houve reprodução; ClimaPrev não necessita multitenancy agora.                                                                                                                                                                        |
| S09 / P2             | [Inicialização backend](/home/ney/Documentos/fullstack/sigfas-server/src/main.ts:22) ativa CORS genérico e Swagger sem condição de ambiente. [Next config](/home/ney/Documentos/fullstack/sigfas-social/next.config.js:61) combina origin `*` com credenciais.                                                                                                                                  | CORS não é autenticação; wildcard com credenciais é incoerente e bloqueado pelo navegador em requisições credenciadas. Controlar exposição operacional por rede e política explícita.                                                                                                                                           |
| S10 / P1             | [Dockerfile backend](/home/ney/Documentos/fullstack/sigfas-server/Dockerfile.prod:17) copia a árvore; não foi encontrado `.dockerignore` nesse backend. [Dockerignore frontend](/home/ney/Documentos/fullstack/sigfas-social/.dockerignore:1) não cobre todas as variantes `.env.*`.                                                                                                            | Arquivo ignorado pelo Git ainda pode entrar na imagem. Revisar contexto e camadas; não afirmar que uma imagem publicada já contém o segredo sem inspecioná-la.                                                                                                                                                                  |
| S11 / P2             | [Helper JWT](/home/ney/Documentos/fullstack/sigfas-social/src/utils/jwt.ts:41) contém persistência de token em localStorage. [Servidor customizado](/home/ney/Documentos/fullstack/sigfas-social/server.js:31) devolve objeto de erro.                                                                                                                                                          | Padrões expõem tokens a JavaScript e podem revelar detalhes. A utilização atual de todos os helpers/rotas não foi comprovada; confirmar alcance antes de classificar exploração.                                                                                                                                                |
| S12 / P2             | [Estratégia JWT](/home/ney/Documentos/fullstack/sigfas-server/src/auth/jwt.strategy.ts:10) não explicita issuer, audience e lista de algoritmos no trecho verificador.                                                                                                                                                                                                                          | Verificar configurações completas da biblioteca/IdP e testar tokens fora do contexto. Não inferir aceitação de qualquer token ou algoritmo.                                                                                                                                                                                     |

Chaves públicas/certificados públicos não são senhas. URLs públicas,
realm e client ID de um cliente público também não precisam ser secretos.
No Next.js, `NEXT_PUBLIC_*` e valores definidos em `next.config.js.env`
podem integrar o bundle. Isso explica por que mover esses valores para `.env`
não os oculta do navegador. A variável chamada `HOST_API_KEY` no Next config
inspecionado representa um endereço, não prova de uma chave de API vazada.
Fontes: [Next.js — ambiente](https://nextjs.org/docs/pages/guides/environment-variables)
e [Next.js — env no bundle](https://nextjs.org/docs/pages/api-reference/config/next-config-js/env).

## Estado do ClimaPrev e lacunas

Registro da inspeção inicial, anterior à implementação parcial T1–T9.
Os links locais do ClimaPrev foram tornados relativos para leitura em outro
checkout; números de linha representam a inspeção original e podem ter mudado.
Consulte `context.md` para o estado após as alterações.

| ID  | Evidência                                                                                                                                                                                                                                                                                                         | Avaliação e destino                                                                                                               |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| C01 | [Gitignore](../../../.gitignore#L6) ignora `.env` e `.homolog/`, mas não `.env.*`; somente `.env.example` aparece rastreado entre `.env*`. [Dockerignore](../../../.dockerignore#L1) usa allowlist, porém a exclusão final não cobre variantes em subpastas permitidas.                                           | P1: ampliar exclusões e testar artefatos; GIT-01, BUILD-01. Não há prova de segredo real ClimaPrev publicado.                     |
| C02 | [Settings](../../../src/climaprev/config.py#L11) já esconde entradas nos erros e guarda senha em atributo privado, mas aceita ambiente arbitrário, senha em URL e produção sem arquivo.                                                                                                                           | P1: validação fechada e requisito obrigatório de secrets; CFG-01, SEC-01.                                                         |
| C03 | [Provisionamento](../../../docker/homolog/provision.py#L8) gera senha aleatória e ACL com default off, mas permite `~climaprev:*` e comandos de inspeção.                                                                                                                                                         | P2: reduzir namespace por ambiente e comandos, com provas reais de Lua, locks e budgets; REDIS-01.                                |
| C04 | [Rate limiter](../../../src/climaprev/infrastructure/rate_limit/redis_rate_limiter.py#L80) inclui IP diretamente na chave. [Identidade](../../../src/climaprev/api/deps.py#L32) já trata proxies confiáveis, mas retorno direto pode não estar canonicalizado.                                                    | P2: HMAC e normalização preservando defesa contra spoofing; IP-01, PROXY-01.                                                      |
| C05 | [Nginx local](../../../docker/frontend/nginx.conf#L5) tem CSP e outros headers, porém não define acesso sanitizado e permite assets por alias genérico. [Homologação](../../../docker/homolog/entrada/nginx.conf#L39) tem TLS e logs mínimos, mas não expõe a busca de localidades nem replica os headers locais. | P1: paridade de rotas, logs e headers; restringir arquivos realmente servidos, sem alegar traversal já explorado. WEB-01, LOG-01. |
| C06 | [Coletor](../../../src/climaprev/log_collector.py#L16) limita tamanho/retenção e campos. A allowlist de rotas ainda não inclui busca.                                                                                                                                                                             | Preservar controles e acrescentar a rota normalizada, não a query. LOG-01.                                                        |
| C07 | [Compose de carga](../../../docker-compose.yml#L160) reutiliza `CLIMAPREV_INMET_ALERTS_BASE_URL`; `.env.example` fornece destino real. app-load compartilha Redis e rede com desenvolvimento.                                                                                                                     | P1: a interpolação pode substituir o mock por INMET real; efeito de rede não foi executado. LOAD-01.                              |
| C08 | [Homolog compose](../../../docker-compose.homolog.yml#L3) isola portas/rede e monta secrets; não tem toda a redução de privilégios do local e usa tags flutuantes. [Dockerfile](../../../Dockerfile#L35) já executa runtime como UID 10001.                                                                       | Preservar UID e limites de rede; aplicar endurecimento testado e digest revisado. NET-01, SEC-01.                                 |
| C09 | [Cliente HTTP](../../../src/climaprev/infrastructure/http/client.py#L51) carrega corpo inteiro; há timeouts, mas não limite explícito de bytes/deadline total. [Lifespan](../../../src/climaprev/main.py#L52) desliga redirects, não explicita `trust_env=False`; não há TrustedHostMiddleware.                   | P2: limitar recursos, fechar destinos e Host. HTTP-01.                                                                            |
| C10 | [CI](../../../.github/workflows/ci.yml#L1) executa testes, lint, tipos e smoke, sem job específico de segredos/vulnerabilidades.                                                                                                                                                                                  | P2: complementar, não substituir os gates existentes. CI-01.                                                                      |
| C11 | [Renderização](../../../frontend/result.js#L40) usa textContent; [API frontend](../../../frontend/api.js#L118) usa caminho de mesma origem.                                                                                                                                                                       | Controle positivo; manter e provar com payload malicioso sintético. Não equivale a auditoria de todo DOM. WEB-01.                 |

## Architecture Overview

Recomendação: evoluir FastAPI + frontend estático + Nginx + Redis existentes,
usando arquivos de segredo por serviço. Não portar frameworks do SIGFAS.

| Alternativa no mesmo escopo                               | Vantagem                                                     | Custo / decisão                                                                   |
| --------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| `.env` para configuração + secrets montados               | Reutiliza homologação, reduz segredo em ambiente de processo | Escolhida; exige proteção do host e disciplina de rotação.                        |
| Cofre externo de segredos + identidade de workload        | Centraliza ciclo de vida e auditoria                         | Evolução futura se hospedagem/equipe justificarem; não escolher fornecedor agora. |
| Credenciais literais em `.env` injetadas como environment | Inicialização simples                                        | Não escolhida para produção: facilita exposição em inspeções e diagnósticos.      |

```text
Navegador: apenas HTML/JS públicos e dados meteorológicos
    |
    | HTTPS (homologação usa CA de teste explícita)
    v
Nginx: rotas/hosts permitidos, headers, limite de body, log mínimo
    |
    | rede de entrada privada; XFF sobrescrito pelo proxy
    v
FastAPI: config validada, cotas, HMAC do IP, erros sanitizados
    |                     |
    | credencial montada  | HTTPS, destinos permitidos, limites
    v                     v
Redis privado + ACL      Provedores meteorológicos

Nginx + FastAPI --metadados--> socket Unix --> coletor sem rede
Operador --provisionamento--> secrets distintos por serviço/ambiente
```

O IP público da entrada continua observável. Um proxy pode evitar acesso
direto à origem, mas só se firewall e publicação de portas também impuserem
essa fronteira. Nome DNS interno ou IP em `.env` não é controle de acesso.

## Code Reuse Analysis

Reutilizar Settings, SecretStr/PrivateAttr, RedisRateLimiter, RedisCache,
RedisLock, ProviderBudget, client_identity, middleware de observabilidade,
coletor e scripts de homologação citados acima. Reutilizar pytest, respx,
Redis real e provider-mock; não criar uma segunda stack de autenticação,
cache ou logging.

Manter separação domínio/aplicação/infraestrutura: identidade de transporte
fica em API/infraestrutura, não em modelos meteorológicos. Não alterar
critérios de risco, unidades, período, geocodificação ou TTLs do forecast.

## Components

### D1 — Git, build e classificação

`.gitignore` receberá `.env.*` com exceção exata para `.env.example`, mantendo
`.homolog/`. Exceções adicionais precisarão de revisão, não wildcard genérico.
`.dockerignore` continuará deny-by-default e excluirá variantes também de
diretórios reabertos. Um teste com sentinelas confirmará imagem, wheel,
contexto de build e diretório estático sem conteúdo secreto.

| Tipo                      | Exemplo de nome, não valor                                       | Destino                                                     |
| ------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| Público                   | caminho `/api/v1/risk`, nomes de provedores, certificado público | Frontend/docs quando necessário                             |
| Interno, não autenticador | subnets, portas, `REDIS_URL` sem senha, hosts permitidos         | `.env` local / configuração do deploy                       |
| Segredo de serviço        | senha Redis, chave HMAC, chave privada TLS                       | Arquivo montado somente no consumidor                       |
| Dado de requisição        | IP, local procurado, coordenadas                                 | Memória e armazenamento mínimo justificado; não logs brutos |
| Identificador de cache    | namespace, versão, digest da previsão                            | Código/Redis; não é uma senha e não precisa ir para `.env`  |

O `.gitignore` contém padrões de arquivos, não um cofre de chaves. A senha
de autenticação Redis é diferente da chave de cache usada para localizar
um resultado. Não retirar a exclusão do `.env` para “habilitar” configuração.

### D2 — contrato de configuração e segredos

Estender Settings, sem carregar automaticamente qualquer `.env` no backend.
O Compose interpola o arquivo escolhido e injeta somente campos explícitos.
Para execução direta, o operador fornece variáveis; não prometer que a
existência de `.env` por si só ativa todas as opções do FastAPI.

| Campo                                      | Contrato proposto                                                                                                                                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLIMAPREV_ENVIRONMENT`                    | Enum development/test/load/production; normalização de espaços/case mantém compatibilidade, demais valores falham.                                                                                  |
| `CLIMAPREV_REDIS_URL` / `REDIS_URL`        | Manter alias legado por compatibilidade, detectar valores divergentes antes de escolher; validar scheme/host/porta/db; nunca password em URL na produção. Username ACL é permitido e não é segredo. |
| `CLIMAPREV_REDIS_PASSWORD_FILE`            | Obrigatório em production; fonte única da senha. Não introduzir variável de senha literal como alternativa.                                                                                         |
| `CLIMAPREV_CLIENT_IP_HMAC_KEY_FILE`        | Novo; obrigatório em production; 32 bytes aleatórios, serializados como 64 caracteres hex; validar formato, decodificar e manter privado.                                                           |
| `CLIMAPREV_ALLOWED_HOSTS`                  | Novo; lista explícita em production, sem `*`. Homologação autoriza localhost e os nomes internos exigidos por healthcheck. Domínio público depende da implantação.                                  |
| `CLIMAPREV_TRUSTED_PROXY_IPS`              | IPs exatos, não `*`, não redes amplas; mudança coordenada com Compose.                                                                                                                              |
| URLs-base dos três provedores              | Em production: HTTPS/443, hostname permitido, sem senha, username, query, fragmento ou IP literal; rejeitar hosts internos conhecidos na allowlist. Não aceitar URL de requisição do visitante.     |
| `CLIMAPREV_PROVIDER_MAX_RESPONSE_BYTES`    | Novo; default 5 MiB, inteiro positivo, teto configurável validado de 64 MiB.                                                                                                                        |
| `CLIMAPREV_PROVIDER_TOTAL_TIMEOUT_SECONDS` | Novo; default 20 s, positivo finito, teto validado de 60 s.                                                                                                                                         |

Segredos não entram em `repr`, model_dump, mensagens de erro, CLI ou métricas.
Não serializar Settings inteiro como diagnóstico. Aliases incompatíveis e
fontes de senha concorrentes são erro, não precedência silenciosa.
Desenvolvimento/test/load podem permanecer sem autenticação Redis e sem HMAC
somente em topologia isolada com dados sintéticos; isso não é equivalente à
produção. Um ensaio com usuários reais exige o perfil protegido.

### D3 — Redis, contêineres e arquivos montados

Estender provisionamento atual para receber ambiente validado (default
production para homologação), gerar senha e chave HMAC independentes e criar
ACL `~climaprev:<ambiente>:*`. Desativar usuário default. Derivar comandos
necessários dos adaptadores; remover SCAN/HGETALL se usados apenas em smoke,
substituindo o teste por chaves conhecidas. Não retirar EVAL sem substituir
atomicidade de locks, cotas e budgets.

Testar recusa de CONFIG, FLUSHALL, ACL, chaves de outro ambiente e operações
equivalentes por Lua; testar também todos os comandos realmente necessários.
Os smokes que usam `homolog-smoke` deverão usar namespace autorizado e chaves
descartáveis com TTL. Não liberar namespace global para facilitar testes.
As ACLs Redis controlam comandos e padrões de chaves; a allowlist final será
validada na imagem pinada. [Referência Redis ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

Preservar Redis sem persistência na stack de cache, sem porta publicada e
sem acesso pelo frontend/coletor. Rede interna Docker não cifra pacotes:
essa proposta assume um host confiável. Redis fora desse host exige TLS com
validação de certificado e revisão da topologia antes do deploy.

Manter diretório de origem 0700. O provisionamento existente usa arquivos
0444 em diretório privado para compatibilidade com file secrets/Podman.
Não aplicar 0600 cegamente: provar leitura pelo UID necessário e isolamento
por montagem; ajustar ownership quando suportado. Nenhum segredo Redis/HMAC
vai para Nginx, e nenhuma chave TLS vai para app ou collector.

Aplicar read-only, tmpfs, no-new-privileges e redução de capabilities por
serviço; exceções mínimas do Nginx/Redis exigem prova de necessidade. Preservar
UID 10001 do runtime. Pin de imagens/digests será resolvido e revisado na
implementação, sem inventar hashes. Esses controles não eliminam acesso do
administrador/root do host.

Compose monta secrets como arquivos com concessão por serviço; isso não
constitui promessa de cifragem do arquivo no host. Não usar build ARG/ENV
para segredos. [Docker — secrets no Compose](https://docs.docker.com/compose/how-tos/use-secrets/).

### D4 — proxy, IP, hosts e superfície pública

Preservar algoritmo de XFF: verificar peer real, limitar 20 entradas, percorrer
da direita para esquerda e selecionar primeiro hop não confiável. Normalizar
também peer direto IPv4/IPv6; para peer ausente usar identidade estável
`unknown`. Cadeia inválida usa peer, nunca uma identidade escolhida pelo
atacante. Uvicorn continua com proxy headers próprios desabilitados.

RedisRateLimiter receberá argumento `identity_key` privado opcional pelo
lifespan; obrigatório em production. Sem chave, o construtor recusará
production mesmo se chamado fora de Settings. Com chave, produzirá:

```text
digest = HMAC-SHA256(chave_exclusiva, "climaprev-ip-v1|ambiente|ip_canonico")
redis_key = "climaprev:ambiente:rate-limit:v2:" + digest_hex
```

Sem chave em perfil não produtivo, manter v1 apenas para dados sintéticos.
Nunca usar SHA simples, base64 ou senha Redis para pseudonimizar IP. HMAC
não é anonimização: chave comprometida permite correlação. O token não será
logado nem devolvido ao usuário. O TTL continua calculado pelo bucket atual.
Todos os workers precisam da mesma chave; não gerá-la por worker.

Na primeira ativação/rotação, v1/v2 antigos expiram por TTL sem flush. Reiniciar
workers de forma coordenada para impedir duas cotas simultâneas durante
rollout. Aceitar e registrar reset transitório de uma cota de burst; se isso
for inaceitável, manter entrada em manutenção durante a transição. Redis fora
do ar mantém 503, sem fallback que ignore limites.

TrustedHostMiddleware valida hosts explícitos, sem confundir Host com origem
CORS ou IP de proxy. CORS fica ausente por padrão na mesma origem, sem
credenciais; lista extra em produção exige origem exata. CORS não bloqueia
clientes não-browser e não substitui autorização.

Rotas públicas propostas: `/`, assets listados, GET/POST `/api/v1/risk`,
GET `/api/v1/locations/search`, GET `/health/live` e `/health/ready` com
conteúdo mínimo. Preservar GET risk enquanto fizer parte do contrato atual.
Docs/OpenAPI e `/internal/metrics` não passam pela entrada. Métricas internas
são acessíveis por operação local autorizada, não por uma URL “difícil”.

Substituir alias arbitrário de assets por allowlist dos arquivos realmente
usados. Validar arquivos ocultos, paths codificados e normalização de URI.
Não transformar erro em fallback para index.html. Limitar body a 16 KiB;
413/404 da entrada podem ter corpo próprio sanitizado, sem fingir que são
envelopes gerados pelo backend.

TLS: manter CA local de homologação com validação explícita, nunca `verify=False`
ou `curl -k`. Para futura produção, exigir certificado válido para o domínio
e firewall antes de expor a entrada. HSTS somente em ambiente público HTTPS
configurado, não na homologação localhost por padrão.

### D5 — logs e frontend

Reaproveitar JSON sanitizado, request ID validado e normalização de rotas.
Adicionar busca à allowlist do coletor e ao map Nginx sem query string.
Nginx local deve desativar acesso bruto ou usar formato mínimo explícito;
nenhum `$remote_addr`, `$request`, `$args`, Authorization ou cookie no log.
Testar também stderr, falhas de upstream, 404, 413, 429 e 500.

Preservar sete dias como teto com coletor ativo, limite por arquivo e expurgo
na retomada. O coletor não é auditoria durável: socket pode perder mensagens
e o host parado não faz limpeza. Não resolver diagnóstico reativando logs
brutos. [OWASP — dados a excluir de logs](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

Aplicar CSP restritiva existente, nosniff, Referrer-Policy,
Permissions-Policy e proteção contra framing em ambas as entradas, inclusive
erros. Preservar renderização por textContent e chamadas relativas. Não
adicionar endpoint `/config`, env.js, armazenamento de tokens ou client secret
no frontend. Localidades/coordenadas retornadas pela funcionalidade continuam
visíveis ao visitante que as consulta; não prometer ocultá-las.

### D6 — destinos e recursos externos

Além das validações de URL, configurar HTTPX com `trust_env=False` e
`follow_redirects=False`. Certificados continuam verificados; uma CA privada
futura requer configuração explícita, não variável herdada silenciosamente.
Não reenviar Authorization/cookie do visitante aos provedores.

No cliente JSON, usar leitura em stream com contador de bytes descomprimidos;
Content-Length não é autoridade suficiente. Limitar a operação completa a
20 s, incluindo tentativas/backoff, liberando response e conexão no finally.
Manter no máximo duas tentativas adicionais para falhas já elegíveis, cota
global consumida por tentativa e ausência de retry automático para 429.
Não repetir resposta grande demais ou redirecionamento.

Redirecionamento e excesso de bytes usam erro sanitizado de provedor
permanente (502); deadline usa indisponibilidade (503). Não adicionar body
externo ao erro. Testar impacto sobre os contratos e o fallback existente.
DNS/allowlist de host não são firewall de saída: proteção contra DNS
comprometido depende da política de egress da implantação, ainda não auditada.

### D7 — carga isolada e CI

O perfil load terá seu próprio Redis e rede internal, somente com app-load,
provider-mock e gerador de carga. As três URLs de provedor serão valores
internos fixos desse perfil, não herdarão variáveis de destinos reais. Manter
cotas/latências de cenário parametrizadas. Validar configuração resolvida
sem imprimir secrets e provar ausência de saída usando destino-sentinela
local controlado; não chamar a internet para comprovar o isolamento.

CI manterá o job existente e terá job de segurança com checkout suficiente
para histórico, detecção de segredos redigida e scan de dependências/imagem.
Usar Gitleaks CLI pinado, com regras padrão mais regras específicas; o
projeto upstream informa manutenção focada em correções de segurança, então
reavaliar suporte na implementação. [Referência Gitleaks](https://github.com/gitleaks/gitleaks).

Para dependências Python, auditar o ambiente resolvido/imagem e não presumir
que qualquer scanner entende o formato customizado de `requirements.lock`.
Trivy pode analisar filesystem/imagem; confirmar inventário detectado e
registrar cobertura. Bloquear HIGH/CRITICAL sem exceção revisada com dono e
vencimento; falha do scanner não equivale a clean. Não declarar CVEs sem scan.
[Trivy — filesystem](https://trivy.dev/docs/latest/target/filesystem/).

PRs não recebem segredos de produção; não usar pull_request_target para
executar código do PR privilegiado. Actions por SHA verificado e ferramentas
por versão/digest. Relatórios exibem regra/local, nunca trecho secreto.
Sentinelas sintéticas testam o gate em repositório temporário, sem criar
commits de segredo no projeto real.

### D8 — operação, senhas e evolução de autenticação

Inventário sem valores: nome, ambiente, finalidade, dono, consumidores,
local de armazenamento, data/versão de rotação e procedimento de revogação.
Senha Redis e HMAC distintos; nenhuma credencial SIGFAS reutilizada.
O cofre externo permanece alternativa futura, não dependência desta entrega.

Se houver segredo válido exposto, primeiro conter e revogar/rotacionar pelo
responsável. Remover literal de código e investigar uso são etapas próprias;
apagar histórico é uma decisão adicional com coordenação e autorização.
[GitHub — remoção de dados sensíveis](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
e [OWASP — ciclo de vida de segredos](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).

Ensaio local de rotação: provisionar nova versão em diretório privado,
validar ACL/arquivos sem exibir conteúdo, parar entrada durante janela curta,
recriar Redis/app com novo material, confirmar senha nova e recusa da antiga,
validar saúde/cotas e reabrir entrada. Cache pode ficar frio; nenhum flush
global. Em falha, manter serviço fechado até configuração válida; nunca
restaurar credencial comprometida. Não sobrescrever diretório existente.

ClimaPrev não recebe login nesta proposta. Se surgirem contas/administração
remota, criar spec própria: identidade por OIDC validada no servidor, issuer/
audience/expiração/algoritmos, autorização por recurso, sessão HttpOnly e
Secure quando aplicável, CSRF quando houver cookies autenticadores,
limitação de tentativas, recuperação com TTL e MFA para operações sensíveis.
CPF, IP, URL escondida e client ID não podem ser usados como senha.

## Risks & Concerns

| Risco / limite                                             | Mitigação e responsável na implementação                                                            |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Credenciais SIGFAS podem estar válidas                     | Proprietário SIGFAS avalia S01–S03 em trabalho separado; não reutilizar nem testar aqui.            |
| Árvores locais sujas e mudanças concorrentes               | Revalidar diff antes de cada tarefa; aplicar alterações pequenas sem formatar arquivos alheios.     |
| Homologação usa environment production                     | Exigir secrets e adaptar fixtures/healthchecks, sem renomear ambiente para escapar da validação.    |
| ACL mínima quebra Lua, locks ou smoke                      | T5/T14 provam operações positivas e negativas no Redis real pinado.                                 |
| Permissões de file secrets variam por engine               | T14 testa UID/mounts; manter diretório privado e não confiar só em mode no YAML.                    |
| HMAC muda a identidade e reseta cotas                      | T7/T18 fazem migração versionada e janela coordenada, preservando TTL.                              |
| Busca deixa de funcionar na homologação                    | T11 prova rota normal e erro junto da proteção de assets.                                           |
| Limite de resposta pode truncar INMET legítimo             | T9 usa fixtures representativas e registra limite escolhido; nunca remover limite silenciosamente.  |
| NAT/Podman rootless agrega clientes no mesmo IP            | Documentar limitação existente; HMAC não recupera IP perdido nem resolve identidade atrás de NAT.   |
| Cache ainda contém localização em valores e algumas chaves | Restringir Redis/TTL; HMAC de IP não cifra cache. Não tratar digest forecast como segredo.          |
| Scanners têm falsos positivos/negativos                    | Testes com sentinelas, triagem sem valores e revisão humana; sem certificação absoluta.             |
| Sem acesso ao ambiente real                                | Publicação depende de verificação externa autorizada de DNS/TLS/rede; planejamento não a substitui. |

## Verificação e entrega

Os testes são especificados por tarefa, usando fixtures sintéticas. Na etapa
inicial de análise foram verificadas documentação, rastreabilidade e links,
sem execução funcional. Depois ocorreram implementação e validações parciais,
registradas em [evidence.md](evidence.md). A execução foi interrompida antes
da conclusão; não confundir o desenho com controles integralmente verificados.

Este diretório segue o planejamento já existente em docs, sem alterar
`.specs/` ou criar outro repositório de notas. As descobertas permanecem aqui
com ponteiros, sem cópias dos segredos ou do código analisado.
