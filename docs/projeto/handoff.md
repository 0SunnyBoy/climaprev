# Handoff de retomada — ClimaPrev

Última continuação: [comparador de chuva e elegibilidade](../operacoes/comparacao-experimental-2026-10-26.md), com 75 testes direcionados e checks estáticos aprovados. Entradas v2, baseline diária, cobertura/exclusões e D+7 ausente explícitos. Sem novo ganho real, campanha ou publicação; checkpoints integrais abaixo são anteriores.

## Continuação de 26/10/2026

Ler o [relatório de implementação](../../RELATORIO-IMPLEMENTACAO-2026-10-26.md). Base remota `5a6fc9c`; lote experimental e alerta 429 ainda locais. 714 testes backend, 33 frontend e checks locais aprovados. Baseline/rodadas, manifesto/ledger e pareamento exploratório de chuva prontos no escopo descrito; campanha e promoção desativadas. Parâmetros finais, outras variáveis, acessibilidade auditiva e publicação do lote continuam pendentes. Registros anteriores são históricos.

## Ler primeiro

[STATE](STATE.md) para validações e estado; [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) para fila; [catálogo](ImplementationsAndRefactoring.md) para caminhos; [refatoração](../operacoes/refatoracao-2026-10-20.md) para o diff transversal.

## Checkout e execução

Branch develop, HEAD/referência local origin/develop em `451d845`; incrementos de responsividade e refatoração ainda locais. Preservar alterações acumuladas e revisar arquivos antes de staging. Não confundir imagem antiga ou CI antigo com o código local atual. Não houve merge/release/deploy.

API/frontend possuem Dockerfiles e Composes próprios; modo integrado local usa `docker compose up -d --build`. Aguardar readiness real, não apenas containers iniciados. Comandos e ambientes estão no README e documentação operacional. Para regressão com Redis usar ambiente isolado de teste, sem flush no banco da aplicação.

## Retomada funcional

O acesso real INMET já foi verificado; acompanhar disponibilidade não equivale a repetir a investigação como bloqueio atual. Leitor de tela aguarda disponibilidade do usuário. Candidate-1 foi retomada no planejamento, com foco em precisão e múltiplos modelos; ainda depende de critérios/proveniência e avaliação independentes. Usuário responsável pelo aceite; responsabilidade não significa aprovação registrada.

Não abrir reservas para escolher ajuste, não promover automaticamente a candidata e não reescrever evidências congeladas. Horizonte de 14 dias e hospedagem adiados. Sem separação de repositórios ou atualização do PDF acadêmico.

## Próximo envio

Revisar diff e arquivos novos, manter .homolog/segredos/dados brutos locais fora do versionamento e executar os gates pertinentes. Conferir CI e Security gates do commit efetivamente enviado. Sem alterações administrativas remotas neste lote.

[Histórico](handoff-HISTORICO-ATE-2026-10-20.md).
