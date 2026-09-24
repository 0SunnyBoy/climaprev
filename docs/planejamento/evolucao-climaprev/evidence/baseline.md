# Baseline: PASS

Commit inicial: 0409f26. `docker compose build`: PASS.
`docker compose run --rm app pytest -q -W error`: **148 passed em 19,85 s**.
A imagem foi construída antes das alterações T1.

As próximas verificações usam o código atual, mesmo antes do rebuild de fim de fase:

```bash
docker compose run --rm -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" app pytest -q -W error
```

Executar na raiz `climaprev`. Redis da stack `climaprev` foi criado nesta sessão e
permanece disponível até a revisão final. Nenhum volume preexistente foi removido.
