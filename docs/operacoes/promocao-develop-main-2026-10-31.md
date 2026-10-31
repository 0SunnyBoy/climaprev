# Promoção develop → main — preparação de 31/10/2026

Autorização do usuário: adaptar o backend no ClimaPrev-API e, após qualificação, integrar develop à main do projeto geral.

## Pré-requisito da API concluído

ClimaPrev-API privado, backend exclusivo, importação `630beba` e correção do gate TLS `225541e26ae526435e7f9eb890073749f7c67d3b`. [API CI aprovado](https://github.com/0SunnyBoy/ClimaPrev-API/actions/runs/41212978380) e [API Security aprovado](https://github.com/0SunnyBoy/ClimaPrev-API/actions/runs/41212978407) nesse SHA. Main e develop do derivado partem dessa versão; namespace `climaprev`, distribuição `climaprev-api`, versão 0.1.0. [Escopo e proveniência](extracao-api-backend-2026-10-31.md).

## Combinação preparada

Base main: `7f1bb3bc91c774d2c68237d89e5968d79314f823`. Fonte develop: `1562f56a55f40a6944d6615a36cc3ce98467b02f`, que acrescenta apenas o registro documental da API ao código funcional já qualificado em `90c61b5`.

Conflitos resolvidos em checkout isolado, sem mudar o checkout develop usado pelo piloto. Mantidos os documentos de contexto atuais, o README e o catálogo atualizados da develop. Descartado o alias antigo `docs/projeto/overview.md`, preservando as visões canônicas em `docs/contexto/`. Preservadas as exclusões de `docker-compose.design.yml` e do plano de números emergenciais internacionais já feitas na main em `c8a577b`. README da main não recomenda arquivo de desenvolvimento ausente; referência histórica ao plano removido foi convertida em texto explícito.

Comparação do índice contra origin/develop: nenhuma diferença em `src`, `frontend`, `tests`, `.github`, Dockerfile, pyproject, locks ou Compose operacional. Assim, a resolução não altera código, regras, contrato, dados ou coletores. 1.319 links locais válidos na verificação anterior a este novo relatório. Qualificação completa da combinação é fornecida pelos checks do branch/PR de promoção; não transferir aprovação para um SHA não conferido.

## Preservação e limites

Reference-v1 permanece padrão; D+7 experimental continua desativado, candidata não promovida, piloto v5 inalterado. Não há deploy, mudança de licença, abertura do repositório privado ou promessa de serviço comercial/SLA. O commit do merge no GitHub registra a promoção efetiva e seus pais; este documento registra a preparação e os critérios.
