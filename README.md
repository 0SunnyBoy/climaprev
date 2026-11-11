# ClimaPrev

Aplicação web para consultar previsões meteorológicas, estimativas de risco e alertas oficiais do INMET. Consulte até sete dias consecutivos entre hoje e os próximos 13 dias, com datas de consulta em UTC. A previsão diária é agregada no fuso da localidade.

## Executar

```sh
docker compose up --build
```

- Interface web em `http://localhost:8080/`.
- API em `http://localhost:8000/`. Use `GET` ou `POST /api/v1/risk` para consultar por cidade ou coordenadas.
- Use `GET /api/v1/locations/search?query=...` para buscar localidades.

## Testar

```sh
docker compose run --rm app pytest -q -W error
```

Os comandos do frontend estão no [guia do frontend](frontend/README.md).

## Documentação

- [Histórico, testes e guia detalhado](docs/contexto/HISTORICO-E-GUIA-CLIMAPREV.md)
- [Arquitetura](docs/arquitetura/arquitetura.md) e [operação](docs/operacoes/operations.md)
- [Diário do piloto](docs/operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md) e [roadmap](docs/projeto/ROADMAP.md)
- [ClimaPrev-API](https://github.com/0SunnyBoy/ClimaPrev-API) e [ClimaPrev-Embedded](https://github.com/0SunnyBoy/ClimaPrev-Embedded)
