# Frontend e backend distintos — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

O repositório continua sendo um monorepo, com unidades de execução e build separadas. Não foram criados repositórios remotos ou alteradas as regras meteorológicas.

## Backend

O backend Python/FastAPI não serve arquivos da interface nem depende de Node. Seu contexto Docker agora exclui a pasta frontend. Para subir somente API e Redis localmente:

```powershell
$env:CLIMAPREV_CORS_ALLOW_ORIGINS='http://localhost:8080'
docker compose -p climaprev-api -f docker-compose.api.yml up -d --build
```

A origem precisa corresponder exatamente à URL usada no navegador (por exemplo, localhost é diferente de 127.0.0.1). Em hospedagem externa, configure também `CLIMAPREV_ALLOWED_HOSTS` com o hostname da API sem scheme/porta. Os Composes locais publicados em loopback não substituem a configuração de TLS/hardening de produção.

O CORS permite GET/POST e o preflight JSON, preserva allowlist sem cookies e expõe `X-Request-ID` e `Retry-After`, necessários para tratar erros/limites entre origens. Isso não adiciona autenticação, quotas por cliente, SLA ou certificação de uma API comercial.

## Frontend

O contexto de build passou a ser exclusivamente `frontend/`; Dockerfile, Nginx, gerador CSP e Compose próprios ficam nessa pasta. Consulte `frontend/README.md`. A CI e homologação foram atualizadas para o novo contexto. O Compose integrado da raiz permanece disponível.

```powershell
Set-Location frontend
$env:VITE_API_BASE_URL='http://localhost:8000'
docker compose -p climaprev-web up -d --build
```

A origem é pública, compilada no bundle, e a configuração Nginx é gerada com a mesma origem. Configuração externa remove rotas proxy e a dependência de DNS do serviço `app`. O modo integrado conserva CSP e proxy na mesma origem. Para Vite fora do Docker, `API_PROXY_TARGET` configura somente o proxy de desenvolvimento, com padrão `http://127.0.0.1:8000`.

## Compatibilidade e limites

Mantidos endpoints/payloads existentes. Frontend valida as respostas na fronteira HTTP. Tipos TypeScript e schemas Python ainda são mantidos separadamente: mudanças incompatíveis exigem atualizar o contrato e seus testes. O domínio continua meteorológico; não houve fitting ou promoção de candidata. A separação em dois repositórios pode ser feita depois, com revisão de CI/contrato e dos caminhos operacionais, mas não é requisito para execução independente.

## Encerramento da validação local

O gate em navegador foi implementado e aprovado no Edge 155.0.4283.62, usando Playwright 1.62.1, com frontend em `https://localhost:8445` e API em `https://localhost:8446`. A API FastAPI e o Redis eram reais; apenas o upstream meteorológico era sintético. O navegador fez busca, POST e exibição do resultado, recebeu 503 com referência, leu os headers de 429 e exibiu cooldown. A origem `https://localhost:8447` foi bloqueada pelo CORS. Com o processo da API parado, a interface continuou acessível e exibiu erro.

Cadeia/hostname TLS foram validados com CA explícita em cliente Node, incluindo rejeição de CA desconhecida e hostname incorreto. O navegador temporário recebeu apenas o pin da chave pública do certificado de teste, limitado ao processo; não foi alterada a confiança global do sistema nem desabilitada genericamente a validação TLS. Esse pin não é uma certificação da cadeia pelo navegador. A separação entre as duas verificações está registrada na evidência.

Evidência: `docs/operacoes/evidence/desacoplamento-browser-2026-10-20.json`. Reprodução: `tests/docker/decoupling/README.md`. O job independente `decoupling` foi adicionado à CI com dependências travadas e salvamento da evidência, mas não foi executado remotamente nesta sessão. O modo integrado também foi reconstruído e aprovado nos gates de HTTP/arquivos estáticos e identidade do proxy.

O desacoplamento de código, build, execução e implantação está concluído e validado nesse escopo local. Não houve publicação ou separação de repositórios. Configuração de domínio, DNS, certificados públicos e homologação da infraestrutura externa continuam sendo atividades de implantação, não pendências de separação do código. Não se declara homologação completa, aprovação científica ou validação de produção.
