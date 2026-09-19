# Rework do frontend

Este documento registra a separação entre a interface web e a API do
ClimaPrev. O frontend continua sendo uma página estática com JavaScript
nativo, mas deixa de fazer parte do pacote Python e passa a ser servido por um
contêiner Nginx.

## Objetivo

Manter o FastAPI como uma API pura e colocar a entrega dos arquivos estáticos
em uma camada HTTP dedicada. Essa separação torna explícito o limite entre a
aplicação Python e a interface, além de alinhar a execução local ao padrão de
homologação planejado.

## Estrutura antes e depois

Antes do rework, os arquivos da interface ficavam em
`src/climaprev/web/`. O FastAPI montava esse diretório em `/assets` e tinha
uma rota `/` que devolvia `index.html`. O `pyproject.toml` também incluía os
arquivos HTML, CSS e JavaScript como dados do pacote.

Depois do rework, a estrutura fica assim:

| Local | Responsabilidade |
| --- | --- |
| `frontend/` | Arquivos estáticos da interface: HTML, CSS e JavaScript. |
| `docker/frontend/nginx.conf` | Entrega do frontend e proxy das rotas públicas. |
| `src/climaprev/` | Código Python da API, sem arquivos da interface. |
| `docker-compose.yml` | Orquestra os serviços `app`, `frontend` e Redis. |

## Alterações realizadas

### Arquivos do frontend

Os arquivos `index.html`, `app.js`, `api.js`, `result.js` e `styles.css`
foram movidos de `src/climaprev/web/` para `frontend/`. Os caminhos usados
pela interface não mudaram: o HTML continua referenciando `/assets/styles.css`
e o JavaScript continua chamando `/api/v1/risk`.

### Backend FastAPI

`src/climaprev/main.py` deixou de importar e usar `Path`, `StaticFiles` e
`FileResponse`. Também foram removidos:

- o mount de `/assets`;
- a rota `/` que retornava `index.html`;
- a resolução do diretório web a partir do pacote Python.

O serviço `app` continua responsável pelas rotas da API, incluindo
`/api/v1/risk`, `/health/live`, `/health/ready` e as rotas internas de
observabilidade. A porta `8000` permanece disponível para chamadas diretas à
API e diagnóstico, mas não entrega mais a interface web.

### Empacotamento Python

O bloco `[tool.setuptools.package-data]` foi removido de `pyproject.toml`. Os
arquivos do frontend não são mais incluídos no wheel nem dependem da
instalação do pacote Python para serem servidos.

### Testes

Na antiga suíte de integração web, foram removidos os testes que verificavam
o FastAPI servindo a página e os assets:

- `test_page_serves_labeled_same_origin_query_form`;
- `test_static_assets_serve_with_correct_media_types`;
- `test_assets_are_available_from_package_directory`.

O teste `test_web_does_not_capture_api_health_or_internal_routes` foi mantido
e passou a ficar em `tests/integration/api/web/test_route_boundaries.py`. Ele
continua verificando que as rotas de saúde e observabilidade permanecem API,
que uma rota inexistente não retorna HTML e que a separação não captura
rotas internas indevidamente.

O teste Docker `tests/docker/test_package_assets.py` permanece fora desse
ajuste e ainda valida assets dentro do wheel. Como o `package-data` foi
removido, esse teste requer revisão em uma etapa posterior caso continue
fazendo parte da suíte executada no CI.

### Nginx

Foi criado `docker/frontend/nginx.conf` com estas regras:

- `GET /` entrega `frontend/index.html`;
- `/assets/...` resolve diretamente os arquivos estáticos em
  `/usr/share/nginx/html`;
- `/etc/nginx/mime.types` associa CSS e JavaScript aos tipos MIME esperados;
- `/api/v1/risk` é encaminhado para `app:8000`;
- `/health/...` é encaminhado para `app:8000`.

O `alias` da localização de assets preserva os URLs existentes no HTML e no
JavaScript. Nenhuma alteração nesses caminhos é necessária.

O arquivo de configuração deve ser salvo em UTF-8 sem BOM. Um BOM antes de
`events {}` faz o Nginx interpretar a diretiva como desconhecida e encerra o
contêiner antes de aceitar conexões.

### Docker Compose

O `docker-compose.yml` ganhou o serviço `frontend`, baseado em
`nginx:1.27-alpine`. Ele monta `./frontend` como somente leitura em
`/usr/share/nginx/html` e monta a configuração do Nginx em
`/etc/nginx/nginx.conf`.

O serviço depende de `app`, usa a rede `local` e publica a porta local
`127.0.0.1:8080`, encaminhada para a porta 80 do Nginx. O serviço `app`
continua publicando `127.0.0.1:8000` para acesso direto à API e debug.

## Fluxo de requisições

| Requisição | Responsável | Resultado |
| --- | --- | --- |
| `http://localhost:8080/` | `frontend` | Entrega `index.html`. |
| `http://localhost:8080/assets/...` | `frontend` | Entrega CSS ou JavaScript. |
| `http://localhost:8080/api/v1/risk...` | `frontend` → `app:8000` | Retorna a resposta JSON de risco. |
| `http://localhost:8080/health/...` | `frontend` → `app:8000` | Retorna o status de saúde da API. |
| `http://localhost:8000/...` | `app` | Acesso direto às rotas da API, sem frontend. |

## Como executar

Suba a stack local com:

```bash
docker compose up --build
```

Abra `http://localhost:8080`. Use `http://localhost:8000` apenas quando
precisar chamar a API diretamente ou diagnosticar o backend.

Exemplos de chamada pela entrada normal do sistema:

```bash
curl "http://localhost:8080/api/v1/risk?location_text=Sao%20Paulo&start_date=2026-08-28&temperature_unit=celsius"
curl "http://localhost:8080/api/v1/risk?latitude=-23.5505&longitude=-46.6333&start_date=2026-08-28&temperature_unit=fahrenheit"
```

## Homologação

Esta alteração atualiza o Compose local e adiciona a configuração do Nginx
para o frontend. A configuração de entrada TLS de homologação continua fora
deste rework; a adaptação de `docker/homolog/entrada/nginx.conf` pode ser
feita posteriormente para aplicar a mesma estratégia de servir estáticos e
encaminhar apenas API e health checks.
