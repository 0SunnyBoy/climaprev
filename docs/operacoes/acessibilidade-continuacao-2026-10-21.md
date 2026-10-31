# Continuação de acessibilidade em 21 de outubro de 2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Correção do alerta de limite de consultas

Na revisão de App.vue, o contador estava fora da região viva em QueryStatus, mas o texto recebido por ela ainda interpolava cooldownSeconds. Consequentemente, o role=alert mudava a cada segundo. O teste isolado de QueryStatus não cobria o texto produzido pelo componente pai.

O aviso passa a usar a espera inicial da resposta 429, mantendo o texto estável até o fim. A contagem visual continua decrementando fora do alerta, com aria-live=off. Quando termina, há mensagem de disponibilidade em role=status e o botão volta a ficar disponível. Troca PT/EN continua traduzindo o aviso sem nova consulta.

Teste de regressão no App cobre 429, estabilidade após um segundo, contador visual, tradução PT/EN, conclusão da espera e ausência de repetição automática de chamada. Validação Docker com o src atual montado: **33 testes frontend, ESLint, vue-tsc e build Vite 6.4.5 aprovados**.

Não houve captura de fala ou execução com leitor de tela real nesta continuação. A correção remove a mudança repetida do DOM identificada; o comportamento auditivo ainda precisa ser observado no leitor/navegador escolhido. Não é certificação WCAG.

## Roteiro auditivo pendente

Registrar sistema, navegador/versão, leitor/versão, idioma, cenário, anúncio observado, foco observado e resultado. Executar PT-BR e EN; não registrar anúncio esperado como se fosse fala realmente capturada.

| Cenário | Ação | Critério a verificar no leitor |
|---|---|---|
| Entrada | Tab e ativação do skip link | Nome do link e foco da consulta; ordem coerente |
| Cidade | Digitar, aguardar, setas e Enter | Campo combobox, lista, opção ativa, seleção e fechamento coerentes |
| Busca vazia/erro | Resposta vazia, falha e repetição | Estados distintos, mensagem percebida, botão acessível após blur |
| Coordenadas | Mudar modo e submeter valores inválidos | Campos ocultos fora da navegação, legendas e erro associado ao campo |
| Datas | Omitir início e informar período fora da janela | Foco no campo e erro associado sem depender apenas de cor |
| Consulta | Submeter, cancelar e simular timeout | Carregamento, cancelamento e falha percebidos; sem resultado tardio sobrescrevendo estado |
| Resultado | Concluir consulta e ativar link do resultado | Resumo, foco e leitura de dias, unidades, fonte e qualidade |
| 429 | Receber limite, aguardar e trocar idioma | Aviso inicial percebido sem interrupção a cada segundo; liberação percebida |
| Alertas | Exercitar disponível, vazio e indisponível | Avisos oficiais distintos do risco; falha não anunciada como ausência de risco |
| Emergência | Abrir e voltar | Mudança de foco, títulos, links tel e conservação do formulário/resultado |
| Preferências | Alternar tema e idioma | Estado/nome coerentes e tradução dos avisos já presentes |

Status da etapa 1: **correção técnica e regressão concluídas; homologação auditiva pendente**. O usuário informou anteriormente não poder testar naquele momento; não há nova evidência de teste realizado.

[Revisão Edge anterior](acessibilidade-edge-2026-10-20.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).
