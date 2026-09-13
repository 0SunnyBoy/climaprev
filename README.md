# ClimaPrev

Interface de consulta e API FastAPI para estimar risco climático de curto prazo. A resposta é uma
estimativa baseada em previsão meteorológica: não substitui alertas oficiais
nem instruções de Defesa Civil, INMET ou autoridades locais.

## Documentação do projeto

Comece por [PROJECT — visão geral e índice](PROJECT.md). Os documentos
detalham [arquitetura](docs/arquitetura.md), [fluxos](docs/fluxos.md),
[informações transmitidas](docs/fluxos-informacao.md),
[segurança](docs/seguranca.md) e [restrições](docs/restricoes.md).
Consulte também o [estado atual](STATE.md) e a [evolução proposta](ROADMAP.md).

## Executar com Docker

```bash
docker compose up --build
```

A interface fica em `http://localhost:8000/`, na mesma origem da API.
Escolha cidade ou coordenadas, período de até sete dias e Celsius/Fahrenheit.
Os resultados mostram dias, qualidade, fonte/coleta, risco estimado e alertas
oficiais em seções separadas. Dados ausentes não viram zero; dados desatualizados
recebem aviso. Erros mantêm o formulário e exigem nova tentativa manual.

A consulta usa JavaScript nativo, sem dependências ou fontes externas, cookies
de identidade, histórico, localStorage ou sessionStorage. A URL da página não
recebe a localização consultada. Sem JavaScript, o botão permanece desabilitado
e a página informa essa necessidade. O formato do campo de data segue o
navegador; a API sempre recebe ISO `YYYY-MM-DD`.

```bash
curl "http://localhost:8000/api/v1/risk?location_text=Sao%20Paulo&start_date=2026-08-28&temperature_unit=celsius"
curl "http://localhost:8000/api/v1/risk?latitude=-23.5505&longitude=-46.6333&start_date=2026-08-28&temperature_unit=fahrenheit"
```

`location_text` ou o par `latitude`/`longitude` é obrigatório. `end_date` é
opcional e o período aceita até sete dias. `temperature_unit` aceita `celsius`
ou `fahrenheit`; só temperaturas são convertidas, não chuva, vento ou umidade.

O endpoint devolve `forecast_risk`, `official_alerts` (por padrão
`not_configured`), `data_quality`, fonte, `request_id` e disclaimer. Erros usam
o envelope estável `{ "error": { "code", "message", "request_id" } }`.
Os códigos usuais são 422 (entrada), 404 (local não encontrado), 429 (limite),
502 (dados inválidos ou requisição rejeitada pelo provedor) e 503 (dependência indisponível).

O 429 do provedor retorna `503 WEATHER_PROVIDER_UNAVAILABLE`, sem retry automático
nessa operação e com fallback apenas dentro do TTL. Outros 4xx externos retornam
`502 WEATHER_PROVIDER_REJECTED`, sem retry nem fallback. Rede, timeout e 5xx têm
até duas tentativas adicionais. Mensagens externas não aparecem na resposta.

Redis reduz chamadas repetidas: previsões frescas duram 10 minutos e podem ser
servidas como `stale` até 15 minutos quando o provedor falha. O limite padrão é
60 requisições/minuto por cliente, com burst de 10. Fontes meteorológicas:
[Open-Meteo Forecast](https://open-meteo.com/) e
[Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api).

## Testes

Todos os testes executam dentro de Docker:

```bash
docker compose build
docker compose run --rm app pytest -q -W error
docker compose run --rm app ruff check src tests
docker compose run --rm app mypy src
```

O roteiro [Browser B01–B10](docs/planejamento/evolucao-climaprev/evidence/browser-tests.md)
registra testes reais em Chrome, cenários controlados, teclado, capturas 360/1280
e validação HTTPS em perfil temporário com CA explícita. Scripts são extraídos
para `/tmp`; não há instalação npm requerida pelo aplicativo.

O smoke de carga é curto e não representa a meta de capacidade. Cada usuário
do Locust é limitado por taxa de chegada a 1 requisição/s; portanto, 100
usuários representam aproximadamente 100 requisições/s após o aquecimento:

```bash
docker compose --profile load build load provider-mock app-load
docker compose --profile load up -d provider-mock app-load
docker compose --profile load run --rm --no-deps load locust -f tests/load/locustfile.py --host http://app-load:8000 --headless --users 2 --spawn-rate 2 --run-time 10s --only-summary
```

O perfil `load` usa o app real, Redis real e um provedor Open-Meteo compatível,
determinístico e interno ao Compose. O serviço `app` padrão continua apontando
para Open-Meteo público. Selecione `CLIMAPREV_LOAD_SCENARIO` antes de subir o
perfil: `warm_cache` usa e prima uma chave fixa, `cold_cache` usa uma chave de
localização única por requisição, `lock_contention` reutiliza uma chave entre
usuários concorrentes, `slow_upstream` atrasa o provider mock e `redis_latency`
atrasa operações Redis apenas no `app-load`. O status 429 é
sempre contado como falha. O mock de carga usa orçamento externo alto, ainda
ativo: capacidade/reposição de 100000 por 60 s. Ajuste com
`CLIMAPREV_LOAD_PROVIDER_BUDGET_CAPACITY`, `CLIMAPREV_LOAD_PROVIDER_BUDGET_REFILL`
e `CLIMAPREV_LOAD_PROVIDER_BUDGET_WINDOW_SECONDS`. Isso se aplica somente ao
`app-load` apontado ao mock; não amplia a cota do Open-Meteo público. Um 503
causado por orçamento esgotado não mede a capacidade de processamento do backend.

O cenário adicional `lock_contention` reutiliza uma chave única entre usuários
concorrentes para medir a contenção do lock distribuído.

Veja [operações](docs/operations.md) para configuração, métricas e baseline.


## Homologação com TLS

O perfil separado usa runtime não root, Redis autenticado, entrada TLS local
e coleta sanitizada com retenção máxima de sete dias. Veja o procedimento e
as limitações de rede em [homologação local](docs/homologacao.md). A CA é
confiada explicitamente; não há publicação externa. Nesse perfil os logs ficam
no volume do coletor, sem stdout persistido pelo engine; o documento mostra
como lê-los e diagnosticar os serviços.
