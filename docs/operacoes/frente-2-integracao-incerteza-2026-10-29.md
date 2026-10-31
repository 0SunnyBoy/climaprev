# Frente 2 — integração da análise de incerteza

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Entrega

Continuidade do incremento local de 28/10. A função `evaluate_development_reports` em `src/climaprev/tools/experimental_uncertainty.py` liga os relatórios v2 do pareamento de chuva à análise por blocos, usando a validação do comparador existente. A nova opção `include_cases` do comparador expõe os pares comuns; o comportamento padrão permanece inalterado.

Entradas explícitas: dois braços, antecedência em dias de coleta, calendário planejado por estação, limites da partição de desenvolvimento, hashes observacionais permitidos, critérios, limiar de evento, blocos, repetições e seed. O calendário é independente da união dos casos relatados: dias e estações omitidos pelos dois braços permanecem no denominador.

Rejeições verificadas: fonte fora da allowlist, alvo fora de desenvolvimento, modelo inesperado, duplicação, divergência de observação, coleta em slots diferentes e inconsistências já tratadas pelo comparador (janela, ponto, antecedência, rodada e exclusões). Relatórios de outras antecedências dentro de desenvolvimento não entram no estrato solicitado. A exigência de rodada pode ser desabilitada explicitamente para controles de rodada desconhecida; isso não estabelece equivalência de antecedência meteorológica.

Saídas: hashes dos relatórios/calendário/pares; comparação comum; sensibilidade agregada e por estação para cada bloco solicitado; suporte, cobertura e diagnóstico de critérios. Nenhum bloco é escolhido automaticamente pelo resultado. Não há ranking, ajuste de pesos, leitura de dados reais ou seleção confirmatória.

## Limites científicos

Verificar o hash declarado contra uma allowlist não autentica o arquivo original nem prova sua autorização. A função exige que o chamador forneça a lista e a partição já autorizadas. Não executar em seleção/confirmação sob o rótulo de desenvolvimento. Não houve abertura de dados reservados nesta rodada.

Os intervalos continuam exploratórios, marginais e sem ajuste de multiplicidade. A sensibilidade de blocos não comprova suporte estatístico; agrupamento por data não certifica independência. Estações com calendários locais distintos exigem revisão do desenho antes da confirmação. Diagnóstico permanece inconclusivo quanto à independência e nunca promove.

O fingerprint da campanha inclui agora incerteza, critérios e bootstrap. Manifestos anteriores não devem ser editados para superar a divergência: gerar e revisar uma nova versão antes de uso. Nenhuma coleta foi ativada.

## Qualificação

71 testes específicos aprovados, com um teste de CLI excluído nessa execução local inicial. A regressão Linux posterior executou a suíte integral, incluindo CLI: **874 testes aprovados**, com warnings como erros, em 197,72 segundos. Ruff dos arquivos alterados e mypy local dos dois módulos de análise aprovados. Mypy integral em Linux aprovado em 90 módulos. Não atribuir a este incremento o CI de commits anteriores. Sem commit/push nesta rodada.

## Pendências reais

1. Revisar/publicar o lote quando solicitado; regressão de 874 testes e mypy Linux de 90 módulos já aprovados.
2. Fechar o plano confirmatório de multiplicidade, suporte e escolha de blocos com diagnósticos de desenvolvimento válidos.
3. Preparar e avaliar variantes de refinamento, congelando versões e parâmetros antes da confirmação.
4. Obter observações recentes e contratos instrumentais elegíveis; executar piloto e confirmação conforme prontidão e calendário revalidado.
5. Integrar candidata apenas após evidência e aceite. Reference-v1 permanece ativa.

F2-05/F2-06 têm avanço técnico, sem encerramento empírico da frente 2 e sem alegação de ganho real.
