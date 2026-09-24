# Spec — segurança, segredos e exposição do ClimaPrev

Estado: T1–T19 implementadas/validadas com dados sintéticos; revisão
independente e validação do ambiente real pendentes. Sem prontidão de produção.
Data: 2026-09-19. Branch: `Atualizacao-Geral-V3`, checkpoint remoto `7ac70d8`.

Atualização de 2026-09-23: CI e Security gates remotos passaram para
`525854a`, sem aceite de produção. Veja o [contexto](context.md) e
[evidências](evidence.md).

[Design e análise comparativa](../../../docs/planejamento/seguranca-configuracao-segredos/design.md) ·
[Tarefas e verificações](../../../docs/planejamento/seguranca-configuracao-segredos/tasks.md).

## Problem Statement

O ClimaPrev precisa proteger credenciais, configurações internas e dados de
requisição de forma consistente em desenvolvimento, carga e homologação.
Mover valores para `.env` é organização de configuração, não criptografia,
controle de acesso ou remoção do histórico Git.

O SIGFAS serve como referência comparativa, não como modelo de segurança
certificado. A inspeção estática encontrou controles úteis, mas também
credenciais literais, configuração de sessão insegura e `.env` rastreado.
O design documenta evidências sem reproduzir senhas, tokens ou IPs privados.

O planejamento foi aprovado para implementação e testes locais. O envio do
checkpoint Git foi autorizado depois. Não inclui rotação de credenciais
reais, publicação de serviços ou mudanças de configuração do GitHub.

## Goals

- Separar configuração pública, configuração interna e segredo.
- Impedir que segredos entrem no Git, build, frontend, logs ou respostas.
- Manter API e Redis internos na homologação; validar a identidade do proxy.
- Reduzir retenção de IP identificável sem enfraquecer o rate limit.
- Isolar testes de carga de provedores reais e do Redis de desenvolvimento.
- Preservar contratos meteorológicos, frontend estático e testes existentes.
- Definir gates verificáveis de segurança e um procedimento de rotação.

## Out of Scope

- Publicar serviços ou alterar credenciais de produção. O envio Git do
  checkpoint foi autorizado posteriormente, conforme o contexto.
- Corrigir o SIGFAS ou testar a validade das credenciais encontradas nele.
- Criar login, usuários, banco SQL, Keycloak, JWT ou sessões no ClimaPrev.
- Garantir anonimato, invisibilidade do IP público ou ausência de falhas.
- Testar sistemas reais, fazer pentest, varredura de rede ou testes de carga
  contra terceiros; auditar todo o histórico remoto ou todos os endpoints
  de negócio do SIGFAS.
- Reescrever histórico, revogar acessos ou apagar caches existentes.
- Certificar conformidade legal ou contratar um cofre de segredos.

## Assumptions & Open Questions

| Assumption                 | Chosen default                                                                               | Rationale                                                                                 |
| -------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Referência SIGFAS          | Backend e frontend de `Documentos/fullstack`, versões registradas no design                  | São as cópias locais relacionadas; não presumir igualdade com produção.                   |
| Base ClimaPrev             | Worktree da branch solicitada, incluindo alterações locais observadas                        | Não sobrescrever trabalho em andamento nem inferir que tudo está commitado.               |
| Autenticação de visitantes | Consulta meteorológica continua anônima                                                      | Não existe requisito de conta; adicionar um IdP aumentaria a superfície.                  |
| Armazenamento de segredos  | Arquivos montados por serviço na homologação; `.env` local ignorado para configuração        | Reaproveita o mecanismo existente e evita credenciais em variáveis do container.          |
| Proteção de IP no Redis    | HMAC obrigatório em `production`, inclusive homologação, com chave exclusiva por implantação | Minimiza identificação direta e mantém cota compartilhada entre workers.                  |
| Perfis sem segredo HMAC    | Permitidos somente em development, test e load, com dados sintéticos                         | Mantém o desenvolvimento utilizável; não promete privacidade equivalente à produção.      |
| Limites de recursos novos  | Body 16 KiB na entrada; resposta externa 5 MiB descomprimidos; operação HTTP externa 20 s    | Ponto inicial mensurável; validar fixtures INMET e previsão antes de aprovação final.     |
| Destino público            | Não definido; manter homologação em loopback                                                 | DNS, certificado público e política de rede são decisões de implantação, não inferências. |
| Dados de evidência         | Somente sintéticos e relatórios redigidos                                                    | A documentação não pode se tornar um novo vazamento.                                      |

Open questions: none para a elaboração deste draft; as decisões externas de
implantação abaixo continuam sendo pré-condições de publicação.

Perguntas resolvidas para este draft: usar arquivos de segredo, manter consulta
anônima e preservar a arquitetura. Não há questão aberta que impeça escrever
os documentos. Antes de qualquer publicação, o responsável deve confirmar
domínio, terminação TLS, topologia de proxy, proprietário dos segredos e
retenção operacional. A publicação fica bloqueada até essa confirmação.

## User Stories

### US1 — manter configuração sem publicar segredos

Como mantenedor, quero configurar o sistema sem colocar credenciais no Git,
na imagem ou na interface.

**Acceptance Criteria**:

1. WHEN arquivos de configuração são preparados para commit, o repositório SHALL ignorar `.env`, variantes `.env.*` e credenciais geradas, permitindo apenas exemplos explicitamente aprovados e sem valores reais. **GIT-01**.
2. WHEN imagens, wheels e assets são produzidos, os artefatos SHALL excluir arquivos secretos e sentinelas de teste, inclusive variantes de `.env` dentro de diretórios permitidos. **BUILD-01**.
3. WHEN a aplicação carrega configurações, ela SHALL aceitar somente `development`, `test`, `load` e `production`, rejeitar ambiguidades de origem e valores inválidos sem ecoar dados sensíveis. **CFG-01**.
4. WHILE o ambiente é `production`, a aplicação SHALL exigir os arquivos de senha Redis e chave HMAC, rejeitar senha em URL/variável literal e recusar iniciar se um segredo estiver ausente, vazio, ilegível ou inválido. **SEC-01**.

### US2 — restringir serviços e preservar cotas

Como operador, quero restringir acesso à infraestrutura e aplicar cotas ao
cliente observado, sem confiar em cabeçalhos arbitrários.

**Acceptance Criteria**:

1. WHILE a homologação executa, a infraestrutura SHALL publicar somente a entrada TLS em loopback, manter API e Redis sem portas publicadas e impedir acesso anônimo ao Redis. **NET-01**.
2. WHEN um cliente Redis autenticado executa operações, a ACL SHALL permitir somente o namespace do ambiente provisionado e comandos necessários à aplicação, recusando outro namespace, administração e acesso sem senha. **REDIS-01**.
3. WHEN a requisição atravessa um proxy, a aplicação SHALL confiar no X-Forwarded-For somente para o peer explicitamente permitido, normalizar IPv4/IPv6 e preservar cotas diante de cadeias malformadas, excessivas ou forjadas. **PROXY-01**.
4. WHILE o ambiente é `production`, as chaves do rate limit SHALL conter HMAC do IP canônico, nunca o IP literal, com resultados iguais entre workers da mesma implantação e diferentes entre implantações com chaves distintas. **IP-01**.
5. IF o Redis falha, THEN a API SHALL manter a resposta de indisponibilidade prevista, sem desativar cotas nem substituir o Redis por contador local permissivo. **REDIS-01**.

### US3 — consultar sem receber ou registrar informação interna

Como visitante, quero usar previsão e busca de localidades sem receber
segredos, dados de infraestrutura ou conteúdo executável do provedor.

**Acceptance Criteria**:

1. WHEN requisições válidas, inválidas ou falhas são processadas, logs e erros SHALL excluir senhas, tokens, IP bruto, cookies, URLs completas, consulta de local e body, preservando apenas metadados permitidos. **LOG-01**.
2. WHILE o coletor está ativo, os logs SHALL respeitar o teto existente de sete dias e arquivos limitados; ao reiniciar, o coletor SHALL remover expirados antes de receber novos eventos. **LOG-01**.
3. WHEN a entrada serve HTTP, ela SHALL permitir apenas rotas e assets aprovados, bloquear arquivos internos com 404 e aplicar cabeçalhos de segurança também nas respostas de erro. **WEB-01**.
4. WHEN dados externos são renderizados, o frontend SHALL manter chamadas de mesma origem, usar texto seguro para nomes e mensagens e não conter credenciais em HTML, JavaScript, storage ou respostas. **WEB-01**.
5. WHEN a API recebe Host não aprovado ou o backend é configurado para um destino externo proibido, o sistema SHALL recusar a operação sem revelar a configuração; em produção os destinos SHALL usar HTTPS, host permitido e nenhuma credencial, query ou fragmento na URL-base. **HTTP-01**.
6. WHEN uma chamada externa excede os limites de tamanho ou tempo, o backend SHALL interromper leitura e liberar recursos, mantendo envelopes sanitizados e limites de retries e conexões. **HTTP-01**.
7. WHEN um body excede 16 KiB na entrada, ela SHALL responder 413 sem encaminhar esse body ao backend. **HTTP-01**.

### US4 — validar e operar a segurança de forma reproduzível

Como mantenedor, quero impedir regressões e conseguir substituir um segredo
sem descobrir o procedimento durante um incidente.

**Acceptance Criteria**:

1. WHEN o perfil de carga inicia, todos os provedores SHALL apontar exclusivamente ao mock, em rede sem saída externa, com Redis separado do desenvolvimento, independentemente de `.env` local. **LOAD-01**.
2. WHEN o CI valida uma alteração, ele SHALL executar detecção de segredos com saída redigida, análise de dependências/imagem e testes de segurança, sem fornecer segredos de produção a código de pull requests. **CI-01**.
3. IF uma credencial potencialmente real é encontrada em código ou histórico, THEN o procedimento SHALL orientar avaliação e revogação/rotação pelo proprietário, sem publicar o valor nem tratar `.gitignore` como remediação suficiente. **OPS-01**.
4. WHEN o ensaio local de rotação termina, a credencial nova SHALL funcionar, a antiga SHALL ser rejeitada e a evidência SHALL registrar impacto, rollback seguro e testes, sem segredos. **OPS-01**.
5. WHILE não existe funcionalidade privada para usuários, o ClimaPrev SHALL manter consultas anônimas e superfícies operacionais internas; uma futura área autenticada SHALL exigir especificação própria antes da implementação. **AUTH-01**.

## Edge Cases

| Caso                                                                              | Resultado obrigatório                                                                               | Requisitos       |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------- |
| `.env.production` dentro de testes/docs; arquivo já rastreado                     | Excluir de build; detectar tracking; não remover histórico automaticamente                          | GIT-01, BUILD-01 |
| Nome de ambiente digitado como `prodution`                                        | Inicialização recusada com mensagem genérica                                                        | CFG-01           |
| Dois aliases Redis divergentes; URL com senha e arquivo simultâneo                | Rejeitar ambiguidade, não escolher silenciosamente                                                  | CFG-01, SEC-01   |
| Senha existente mas vazia, arquivo inacessível ou HMAC curto                      | Não iniciar `production`; não imprimir conteúdo/caminho sensível                                    | SEC-01           |
| IPv6 em formas equivalentes; peer ausente; mais de 20 hops; XFF inválido          | Canonicalizar; fallback para peer/identidade desconhecida estável; nunca confiar no prefixo forjado | PROXY-01, IP-01  |
| Rotação HMAC com workers antigos vivos                                            | Não misturar versões; reinício coordenado e reset controlado de cota documentado                    | IP-01, OPS-01    |
| Falha Redis; comando permitido via Lua em chave proibida                          | 503 sanitizado; ACL recusa inclusive a operação Lua                                                 | REDIS-01         |
| `.env`, `.git`, config Nginx, docs ou metrics solicitados por aliases/codificação | 404 pela entrada; não servir por fallback de SPA                                                    | WEB-01           |
| Busca com nome malicioso ou HTML no provedor                                      | Texto inerte; nenhum script executado                                                               | WEB-01           |
| HTTP 302, URL-base com query, Host adulterado, proxy herdado do processo          | Rejeitar redirecionamento; validar destino/Host; não herdar proxy ambiente                          | HTTP-01          |
| Chunked/compressão sem Content-Length; resposta muito lenta                       | Contar bytes descomprimidos em stream; deadline por operação, fechar conexão                        | HTTP-01          |
| `.env` aponta INMET real durante carga                                            | Destino permanece mock, sem rota de rede externa                                                    | LOAD-01          |
| Coletor parado por mais de sete dias                                              | Expurgo na retomada; não afirmar remoção física enquanto parado                                     | LOG-01           |
| Scanner indisponível ou relatório sem redigir                                     | Gate não aprova; não anexar relatório bruto                                                         | CI-01            |
| Root/administrador do host lê secrets montados                                    | Limitação explícita do modelo; não prometer proteção contra administrador comprometido              | SEC-01, OPS-01   |

## Requirement Traceability

| ID       | Requirement                              | Design     | Tasks                  | Status   |
| -------- | ---------------------------------------- | ---------- | ---------------------- | -------- |
| GIT-01   | Exclusão de segredos no Git              | D1         | T1, T16, T17           | verified |
| BUILD-01 | Artefatos sem segredos                   | D1, D7     | T2, T15, T17           | verified |
| CFG-01   | Configuração fechada e sem ambiguidade   | D2         | T3, T4                 | verified |
| SEC-01   | Segredos por arquivo e privilégio mínimo | D2, D3     | T3, T4, T5, T8, T14    | verified; host admin remains trusted |
| NET-01   | Exposição restrita e TLS                 | D3, D4     | T10, T11, T13, T14     | verified in synthetic homolog; real edge pending |
| REDIS-01 | Autenticação, ACL e falha segura         | D3         | T5, T7, T8, T14        | verified |
| PROXY-01 | Identidade confiável e canônica          | D4         | T6, T10, T11, T13, T14 | verified |
| IP-01    | Pseudonimização no rate limit            | D4         | T4, T5, T7, T8, T14    | verified in synthetic homolog |
| LOG-01   | Logs minimizados e retenção              | D5         | T10, T11, T12, T14     | verified |
| WEB-01   | Frontend e fronteira HTTP seguros        | D4, D5     | T10, T11, T15          | verified |
| HTTP-01  | Destinos, hosts e recursos limitados     | D2, D4, D6 | T4, T8, T9, T10, T11   | verified |
| LOAD-01  | Carga sem produção/terceiros             | D7         | T13, T17               | verified |
| CI-01    | Gates preventivos                        | D7         | T16, T17, T19          | verified in local and remote CI |
| OPS-01   | Rotação e resposta a exposição           | D8         | T18, T19               | verified synthetically; real incident pending |
| AUTH-01  | Fronteira pública versus operacional     | D4, D8     | T8, T10, T11, T18      | verified |

## Success Criteria

A implementação do ciclo T1–T19 tem evidência nos gates locais e remotos.
Isso não equivale a autorização de produção: os requisitos marcados como
dependentes da borda real precisam ser confirmados pelo operador responsável
antes da publicação.
Nenhum segredo real será usado em testes. Uma falha ou teste não executado
será registrado como pendência, nunca como aprovação.

Para esta entrega de planejamento, sucesso significa os três documentos
coerentes, fontes localizáveis, tarefas rastreáveis e validação estrutural.
Isso não significa que o projeto já recebeu as proteções propostas.
