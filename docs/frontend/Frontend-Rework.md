# Frontend Rework

## Objetivo

O frontend do ClimaPrev foi migrado de JavaScript nativo com manipulação
imperativa do DOM para Vue 3 com TypeScript estrito e Vite. A migração mantém o
contrato público da API, a linguagem visual, os requisitos de acessibilidade e
os fluxos de consulta existentes.

## Stack atual

- Vue 3 com Composition API;
- TypeScript em modo `strict`;
- Vite para desenvolvimento e build;
- Vitest para testes unitários;
- ESLint com suporte a Vue e TypeScript;
- Nginx como runtime estático;
- Docker multi-stage: Node compila e Nginx serve somente `dist`.

## Estrutura

```text
frontend/
  src/
    components/
      DataQualityNotice.vue
      ForecastDayCard.vue
      ForecastResult.vue
      LocationAutocomplete.vue
      OfficialAlerts.vue
      QueryForm.vue
      QueryStatus.vue
      RiskSummary.vue
    composables/
      useLocationSearch.ts
      useRiskQuery.ts
    services/
      api.ts
      api.test.ts
    types/
      api.ts
      query.ts
    utils/
      formatters.ts
    App.vue
    main.ts
  index.html
  styles.css
  package.json
  package-lock.json
  tsconfig.json
  vite.config.ts
  vitest.config.ts
  Dockerfile
```

## Responsabilidades

`App.vue` coordena o fluxo da tela, o status da consulta, o cooldown de rate
limit e a integração entre formulário e resultado.

`QueryForm.vue` preserva os campos de cidade, coordenadas, período e unidade de
temperatura. A validação nativa do navegador continua sendo utilizada, com a
regra adicional de período máximo de sete dias.

`LocationAutocomplete.vue` e `useLocationSearch.ts` isolam o debounce, o
cancelamento da busca anterior e a seleção de localidades.

`useRiskQuery.ts` encapsula timeout de dez segundos, cancelamento, substituição
de requisições antigas e descarte de respostas obsoletas.

`services/api.ts` é a fronteira de rede. Ele mantém requisições same-origin,
`credentials: omit`, `POST` para risco, validação runtime da resposta e
tratamento tipado de erros.

`ForecastResult.vue` compõe os componentes de qualidade dos dados, risco,
previsão diária e alertas oficiais. A renderização usa interpolação Vue, sem
`innerHTML` ou execução de conteúdo recebido da rede.

O `styles.css` existente foi preservado como folha global e importado pelo
entrypoint Vue para manter a identidade visual durante a migração.

## Build e execução

Na pasta `frontend/`:

```bash
npm ci
npm run typecheck
npm run lint
npm run test
npm run build
```

O build gera `frontend/dist/`. A imagem `frontend/Dockerfile` executa esse
build em uma etapa Node e copia somente os arquivos estáticos para uma imagem
Nginx final. O `docker-compose.yml` constrói essa imagem e publica a interface
em `127.0.0.1:8080`.

O Nginx serve `/` e `/assets/` e encaminha apenas as rotas públicas de API e
health previstas na configuração. Os nomes de assets são gerados pelo Vite e
podem conter hash; por isso os testes descobrem os recursos a partir do HTML,
em vez de depender de nomes fixos.

O Compose de homologação também constrói a imagem `frontend/Dockerfile` e
monta apenas sua configuração de entrada TLS. Assim, local e homologação usam
o mesmo `dist`, enquanto cada ambiente mantém seu próprio proxy e política de
transporte.

## Paridade preservada

- consulta por cidade;
- consulta por coordenadas;
- autocomplete de localidades;
- período de até sete dias;
- Celsius e Fahrenheit;
- timeout e cancelamento;
- proteção contra respostas antigas;
- tratamento de rede, validação, indisponibilidade e rate limit;
- identificação da requisição;
- fonte, horário e qualidade dos dados;
- previsão desatualizada;
- separação entre risco estimado e alerta oficial;
- navegação por teclado, foco e live region;
- responsividade e ausência de armazenamento local da consulta.

## Verificações executadas

- `npm run lint`;
- `npm run typecheck`;
- `npm run test`;
- `npm run build`;
- teste estático de segurança do frontend;
- teste do contrato de `POST /api/v1/risk`;
- validação de identidade e proxy Nginx local;
- `docker build -f frontend/Dockerfile .`;
- `nginx -t` dentro da imagem com o alias de rede necessário para o upstream
  Docker `app`.

## Decisões de escopo

Pinia, Nuxt, biblioteca visual pesada, autenticação, histórico e notificações
não foram introduzidos. O estado atual é local à tela e aos composables; uma
store global só será adicionada quando houver mais de uma tela ou estado
compartilhado real.
