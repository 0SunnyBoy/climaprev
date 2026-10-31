# Responsividade — primeiro incremento de 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Conclusão da etapa 1 no escopo local

Medição controlada, recuperação e revisão responsiva concluídas neste lote. A etapa 1 fica concluída como qualificação local de responsividade/recuperação, não como certificação de capacidade, disponibilidade ou desempenho de produção. Sem mudança de timeout/backend ou concorrência especulativa. Permanecem acompanhamento dos provedores e medição no futuro ambiente, além da etapa 2 de acessibilidade auditiva.

### Incremento complementar

A consulta principal também passa a encerrar sua promise em timeout/cancelamento mesmo se o transporte ignorar abort. O prazo permanece dez segundos. O resultado atrasado não substitui o erro ou a consulta atual. Testes cobrem transporte travado, cancelamento explícito, troca de consulta e desmontagem. Textos PT/EN dos dias de maior risco passam a atender uma ou várias datas.

Validação atual: **31 testes frontend**, build/tipagem/ESLint aprovados; **34 testes backend selecionados** de prazo/cache/contrato aprovados. Backend sem alteração; esses 34 não representam reexecução dos 651 testes totais anteriores. Build/tipagem/lint também aprovados após ajuste textual final.

### Cache controlado e falhas

Aplicação ASGI separada, provedores HTTP reais, Redis DB 14 com namespace aleatório próprio para cache e lock. Não houve flush nem alteração do cache da aplicação em execução. Foram feitas três duplas fria/repetida; conexões HTTP podem ser reutilizadas, portanto cache frio não implica conexão fria. [Resultados por etapa](evidence/responsividade-controlada-2026-10-20.json).

| Cidade | Fria | Repetida | Previsão na fria | Avisos na fria |
|---|---:|---:|---:|---:|
| Belém | 2.155,66 ms | 3,92 ms | 653,37 ms | 1.467,75 ms |
| Brasília | 1.203,68 ms | 3,57 ms | 177,21 ms | 1.023,56 ms |
| Porto Alegre | 1.413,39 ms | 4,21 ms | 163,27 ms | 1.246,33 ms |

Todas retornaram HTTP 200, dados completos/não obsoletos e integração de avisos disponível. Falha de transporte injetada no provedor, sem cache elegível: 503 em 4,51 ms. Provedor travado injetado: 503 em 7.005,73 ms, com cancelamento confirmado. Falhas injetadas não são incidentes dos provedores reais. Amostra pequena e sequencial; sem percentis ou inferência de capacidade. INMET dominou a latência fria nesta amostra; não se conclui que seja causa de todos os timeouts anteriores. Não se justifica aumentar orçamento com esses dados.

### Navegador e layout

Frontend reconstruído e saudável; inspeção interativa no navegador integrado. Formulário e resultado sem overflow horizontal em 320, 375, 768 e 1280 px; resultado inglês também verificado a 320 px. Consulta real de um dia e de sete dias para Belém retornou dados completos; link para resultado moveu foco para `result`. Indicador de espera e botão cancelar visíveis durante requisição. Revisão visual mobile realizada; não equivale a ensaio em aparelhos físicos ou leitor de tela. [Captura mobile](evidence/responsividade-mobile-2026-10-20.png).

## Entrega

A busca de cidades não possuía prazo próprio no frontend. Após o debounce de 250 ms, passa a ter prazo de cinco segundos: aborta o transporte, encerra o indicador de espera e apresenta a recuperação existente em PT/EN. Uma corrida de promises permite encerrar mesmo se o transporte não concluir ao receber abort. Cancelar, digitar novamente ou desmontar limpa o prazo; respostas antigas não substituem o estado atual.

Não modifica o prazo de dez segundos da consulta meteorológica nem o orçamento de sete segundos do serviço. Não implica promessa de resposta em cinco segundos: é limite da espera da busca no cliente, sujeito ao agendamento do navegador.

## Validação

- 29 testes de frontend aprovados, incluindo requisição que nunca resolve, abort, repetição e resposta tardia.
- Build, tipagem e ESLint aprovados em container com o código fonte atual montado.
- Sem alteração de backend neste incremento; suíte backend não reexecutada.
- Ensaio auditivo com leitor de tela continua pendente; usuário indisponível para executá-lo. Testes automatizados não o substituem.

## Medição real local

Quatro requisições sequenciais dentro do container da aplicação, em 20/10/2026 às 18:24 UTC, usando os provedores configurados. Cache não expurgado. Busca `Belem`: HTTP 200 em 965,77 ms e 234,28 ms. Previsão para coordenadas de Belém e data 20/10: HTTP 200 em 2.330,32 ms e 6,91 ms; ambas com dados completos, não obsoletos, fonte Open-Meteo, mesmo fetched_at `2026-10-20T18:24:00.221024Z`.

A tentativa inicial a partir do host restrito foi bloqueada por permissão de socket; esse resultado não mede o serviço. Registro em [evidência](evidence/responsividade-amostra-2026-10-20.json). A repetição via Docker conseguiu acesso. Não é benchmark frio, teste de carga, comparação antes/depois ou comprovação de ganho na API. A correção afeta recuperação do frontend e não acelera o provedor.

## Continuação

Continuar preparação científica e seleção de modelos conforme RDP, sem tratar licença, critérios ou promoção como aprovados. O serviço consulta previsão e avisos em sequência; eventual otimização futura precisa preservar cancelamento, expiração e a semântica de fuso. Ampliar amostragem se novos incidentes ou mudanças justificarem; medições de capacidade ficam para o ambiente definitivo.
