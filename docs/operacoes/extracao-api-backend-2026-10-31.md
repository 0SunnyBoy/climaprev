# Backend independente ClimaPrev-API — 31/10/2026

## Entrega

Destino privado: [0SunnyBoy/ClimaPrev-API](https://github.com/0SunnyBoy/ClimaPrev-API). O repositório estava vazio: recebeu uma importação seletiva do backend, não um merge de históricos não relacionados. Primeira versão: `630beba6186910d45e82dde479b587d6c4c5a6eb`, originada do ClimaPrev `90c61b5a458f293c4bc02ca0497cf48f2fa85469`.

Distribuição Python `climaprev-api` 0.1.0, mantendo imports `climaprev`. Inclui somente backend operacional, testes necessários, build/CI, configuração, documentação e proveniência próprios. São 51 módulos; frontend, Node, ferramentas científicas, coletas/D+7 experimental, observações, dados reservados, credenciais e arquivos locais não foram importados.

## Funcionalidade e diferenças

Preservados GET/POST de risco, busca de localidades, saúde, CORS, erros/request IDs, limites/resiliência, cache/Redis, avisos oficiais e política reference-v1. Contrato 14/7 mantido; OpenAPI canônico `474199bf4155eec9bde52b4343e0aaed12888bee7315f9e87460b48efaac62fe`.

Composição da API não carrega candidata científica; configuração de bundle experimental é recusada explicitamente. A pesquisa permanece neste monorepo. Não houve promoção da candidate-1, mudança da política ou alteração do piloto.

Docker/Compose autônomos, sem `extends`, frontend ou arquivos do projeto geral. Imagem de produção não root, UID10001, sem ferramentas de desenvolvimento; Redis interno. O perfil local liga a API ao loopback e é desenvolvimento. Produção exige configuração/credenciais/TLS próprios. Exemplo de proxy HTTPS bloqueia métricas internas e foi exercitado com cliente externo.

`UPSTREAM.json` registra allowlist, hashes de origem/destino e exclusões; `.gitattributes` preserva os bytes entre plataformas. Atribuições e autoria original são mantidas. Licença, condições comerciais dos provedores, gestão de clientes e SLA não são resolvidos pela separação.

## Validação própria

- **550 testes operacionais aprovados**, Ruff e mypy em **51 módulos**, em Linux.
- Build do pacote/imagem independente, instalação sem frontend/pesquisa, runtime UID10001 e ausência de ferramentas de desenvolvimento verificados.
- HTTP e HTTPS, CORS permitido/negado, saúde, envelope de erro e fronteira de métricas internas aprovados.
- Consulta climática real de um dia: HTTP200, reference-v1, Open-Meteo e avisos oficiais disponíveis. Diagnóstico de disponibilidade, não comprovação de precisão.
- Gitleaks: detector sintético validado e histórico do snapshot sem achados. O campo ambíguo `api_sha256` do manifesto foi renomeado para `destination_sha256`; não houve exclusão de caminhos ou enfraquecimento do scanner.
- Trivy: execução local com zero achados HIGH/CRITICAL na imagem final.

Checks próprios do SHA da API: [API CI](https://github.com/0SunnyBoy/ClimaPrev-API/actions/runs/41212978380) e [API Security](https://github.com/0SunnyBoy/ClimaPrev-API/actions/runs/41212978407). Suas conclusões devem ser conferidas antes da promoção do projeto geral; checks do monorepo não substituem os da distribuição independente.

Correção de CI posterior à importação: `225541e26ae526435e7f9eb890073749f7c67d3b` aguarda prontidão do proxy HTTPS com retries limitados, IPv4 explícito e validação de certificado preservada. O primeiro CI passou os gates de aplicação e encontrou apenas uma corrida de inicialização TLS; o backend não foi alterado para contornar o teste.

## Continuidade

Manter o ClimaPrev completo neste repositório e a API operacional no derivado. Próximas sincronizações devem registrar SHA, adaptar a composição quando necessário e repetir testes/contrato/segurança. Não copiar snapshots/coletores/candidatas por conveniência. A API tem main própria; a promoção develop→main do projeto geral é uma operação separada, condicionada à qualificação dos dois repositórios.
