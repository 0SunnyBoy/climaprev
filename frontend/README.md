# ClimaPrev — frontend

> **Revisão contextual — 30/10/2026.** [Estado vigente](../docs/projeto/STATE.md) · [RDP](../docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../docs/operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Versão 0.1.0 em desenvolvimento. Estado e validações no [STATE](../docs/projeto/STATE.md), pendências no [RDP](../docs/contexto/RELATORIO-PENDENCIAS-2026-10-20.md). Transporte e validação runtime separados; prazo/cancelamento compartilhado entre busca e consulta. Acessibilidade auditiva continua pendente.

Aplicação Vue/TypeScript independente, que consome a API HTTP/JSON `/api/v1`. Esta pasta contém dependências, testes, build, Dockerfile, configuração Nginx e Compose próprios. O código Python não é necessário para construir a interface.

## Desenvolvimento local

Execute nesta pasta: `npm ci --ignore-scripts` e `npm run dev`. Por padrão, Vite encaminha as chamadas para `http://127.0.0.1:8000`. Para outro backend, configure `API_PROXY_TARGET` em `.env.local`; essa variável pertence apenas ao servidor de desenvolvimento. A API pode ser executada separadamente seguindo `docs/arquitetura/desacoplamento-2026-10-20.md` na raiz do projeto.

## API em origem diferente

Configure `VITE_API_BASE_URL=https://api.exemplo.com` antes de `npm run build`. Aceita somente origem HTTP(S), sem caminho, credenciais, query ou fragmento. O `/api/v1` continua definido no cliente. Essa variável é pública e incorporada ao bundle: mudar o destino exige reconstruir a interface. Não inclua segredos nela.

Para Docker, defina a mesma variável no ambiente e execute `docker compose -p climaprev-web up -d --build` nesta pasta. O Compose próprio exige a origem da API e não inicia um backend. A imagem gera CSP permitindo conexão à origem exata configurada e remove os proxies que dependiam do hostname Docker `app`. HTTPS no navegador requer API HTTPS para evitar bloqueio por conteúdo misto. O Compose local publica apenas em `127.0.0.1:8080`; exposição externa/TLS deve ser configurada no ambiente de implantação.

Para hospedagem estática externa, publique `dist/` e configure no host a CSP equivalente; o gerador Nginx é executado pelo Dockerfile, não pelo simples `npm run build`.

O backend deve permitir explicitamente a origem da interface via `CLIMAPREV_CORS_ALLOW_ORIGINS` e aceitar seu próprio hostname via `CLIMAPREV_ALLOWED_HOSTS`. Não habilite wildcard em produção. O cliente não envia cookies e não implementa autenticação de consumidores.

## Modo integrado existente

Sem `VITE_API_BASE_URL`, a interface usa URLs relativas. O Compose da raiz mantém Nginx encaminhando à API na mesma origem, sem precisar de CORS. O Compose de design injeta `API_PROXY_TARGET=http://app:8000`. Os dois modos preservam o mesmo contrato da API.

Validação: `npm test`, `npm run lint` e `npm run build`.

Validação end-to-end do desacoplamento: `tests/docker/decoupling/README.md` na raiz. O gate aprovado usa API real em outra origem HTTPS, verifica erros/CORS/cooldown e funcionamento da interface durante parada da API. Não exige separar repositórios.

## Manutenção de 30/10/2026

`App.vue` reutiliza `toRiskQueryPayload`; o formulário compartilha o mesmo limite final entre o campo e a validação. 61 testes frontend, lint, tipagem e build aprovados com Node.js 22. [Relatório transversal](../docs/operacoes/refatoracao-controle-d7-2026-10-30.md).
