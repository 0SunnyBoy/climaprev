# Verificação de entrega dos avisos

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Continuação de 26/10/2026, após o relato do usuário de observar somente vento forte. Escopo: confirmar regras, transporte pela API e renderização de condições sintéticas, sem alterar limiares ou fabricar um alerta real.

## Resultado

Chuva horária/diária, sinal de alagamento derivado da chuva, rajadas, calor e frio estão ativos na reference-v1. Não foi encontrado filtro de interface que permita apenas vento. Umidade não possui regra própria de risco. Avisos INMET são outra camada e não foram consultados ao vivo nesta verificação.

Novos testes da rota POST usam o caso de uso e o avaliador reais com previsão, cache e locks controlados em memória; apenas upstream e rate limit são substituídos na aplicação de teste. Verificam chuva horária, diária, vento, calor, frio, dado parcial e condições simultâneas, em Celsius/Fahrenheit. Condições e classificação são preservadas tanto no resumo do período quanto no dia da resposta JSON.

Testes Vue montados em DOM simulado verificam os rótulos de todas as condições em PT/EN, coexistência sob prioridade de aviso oficial, preservação de risco com dados parciais e distinção entre feed oficial indisponível e feed disponível sem itens. Não é uma sessão de navegador com servidores reais nem teste auditivo com leitor de tela.

## Correção de apresentação

O resumo de risco passava as unidades internas `celsius`/`fahrenheit` diretamente ao texto. Corrigido para usar o formatador existente e exibir **°C/°F**, preservando o valor recebido e sem reconversão ou alteração dos critérios de risco.

## Validação

- 32 testes backend selecionados aprovados: 14 cenários integrados de entrega pela rota e 18 testes de política/avaliação.
- 48 testes frontend aprovados, incluindo 15 novos casos de apresentação; ESLint, vue-tsc e build Vite aprovados na versão final.
- Ruff do novo teste e `git diff --check` aprovados.
- Primeira tentativa de tipagem dos novos testes encontrou uso indevido de `get().exists()`; corrigido para verificar o texto esperado, e validação repetida com sucesso.
- Última regressão backend completa permanece o checkpoint anterior de 714 testes, registrado no [relatório científico/técnico](../contexto/RELATORIO-IMPLEMENTACAO-2026-10-26.md). A nova rodada backend foi direcionada, sem reexecutar toda a suíte.

Alterações locais, sem commit/push ou CI remoto deste incremento. Não foi identificada a causa da consulta específica vista pelo usuário: cidade, período e resposta original não foram fornecidos. A hipótese de limiar não atingido ou dado ausente não foi tratada como diagnóstico confirmado. Sem mudança na reference-v1, novos tipos de risco, janela pública, campanha ou promoção.
