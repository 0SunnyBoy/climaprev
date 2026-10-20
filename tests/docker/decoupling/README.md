# Gate de desacoplamento HTTPS

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../../../docs/projeto/STATE.md) e o [RDP atualizado](../../../RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Bancada exclusiva de teste: frontend estático, backend FastAPI real, Redis próprio, upstream meteorológico sintético e duas entradas TLS locais. Não usa serviços/dados de produção. Não modifica repositórios remotos ou confiança global de certificados.

## Preparação

Na raiz do projeto:

1. `docker compose -f tests/docker/decoupling/compose.yaml build api`. A bancada usa a imagem explícita `climaprev-api:decoupling-e2e` para API/provedor, sem depender do nome da pasta ou do projeto Compose principal.
2. Criar `.homolog/decoupling/` (0700 em Linux). Gerar certificados com `python docker/homolog/entrada/provision_tls.py .homolog/decoupling` se OpenSSL estiver instalado. No Windows, pode-se usar o wrapper `python docs/operacoes/scripts/provision_tls_with_container.py .homolog/decoupling`, com a imagem `climaprev-openssl-test:local` previamente construída pelo Dockerfile operacional existente. O provisionador protege ACL e recusa sobrescrever certificados.
3. `docker compose -f tests/docker/decoupling/compose.yaml up -d --build --wait`
4. `npm ci --ignore-scripts --prefix tests/docker/decoupling`
5. `node tests/docker/decoupling/node_modules/playwright/cli.js install chromium` (em Linux instalar dependências com `--with-deps`).

## Execução

Defina `PLAYWRIGHT_MODULE` como caminho absoluto de `tests/docker/decoupling/node_modules/playwright/index.mjs`. Opcionalmente, `BROWSER_EXECUTABLE` pode apontar para Edge/Chromium local; omitida, usa o Chromium instalado pelo Playwright. Execute `node tests/docker/check_decoupled_browser.mjs` na raiz.

O teste valida cadeia/hostname TLS com a CA explícita, rejeita CA desconhecida e hostname divergente. O navegador temporário confia somente na chave pública do certificado de teste por pin SPKI restrito ao processo. Essa confiança não equivale a validar a cadeia pelo navegador: essa parte é verificada separadamente pelo cliente TLS Node. Não se usa `ignoreHTTPSErrors`, desabilitação global de validação TLS ou alteração do trust store do Windows.

Frontend: `https://localhost:8445`; API: `https://localhost:8446`; origem rejeitada: `https://localhost:8447`. O teste não intercepta/forja respostas de API no navegador: faz busca, POST, falha do provedor, rate limit real e parada do backend. A bancada limpa somente o Redis dedicado de testes. Ao terminar, grava evidência em `docs/operacoes/evidence/desacoplamento-browser-2026-10-20.json` e restaura processos parados por ele.

Encerre com `docker compose -f tests/docker/decoupling/compose.yaml down -v`. A CA e chaves locais ficam ignoradas pelo Git. O job `decoupling` da CI reproduz a bancada; ter o job configurado não comprova execução remota aprovada.
