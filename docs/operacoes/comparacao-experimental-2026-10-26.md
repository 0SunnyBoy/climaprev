# Comparação experimental e elegibilidade

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Continuação local de 26/10/2026. Entregas: comparação exploratória consolidada de chuva, controles de elegibilidade temporal e entrada da baseline diária. Sem coleta recorrente, leitura de novos outcomes reservados, fitting ou promoção. Reference-v1 e janela pública inalteradas.

## Implementações

- Pareamento evoluído para `climaprev-station-rain-pairs-v2`: coleta UTC, inicialização opcional, dias após coleta e horas da inicialização até o alvo. Inicialização não pode seguir a coleta. Nenhum horário desconhecido é inventado.
- `pair_baseline_rain` compara diretamente o acumulado diário normalizado pelo adaptador vigente com a observação da estação. Não distribui esse total entre horas; preserva a seleção automática desconhecida, lacunas e cobertura insuficiente. Guarda a identidade da baseline.
- `experimental_comparison.compare_rain_models` exige estação/coordenadas/fuso, intervalo civil, observação e fonte compatíveis, com controle de duplicatas e valores não finitos/negativos. Recalcula a cronologia e o horizonte de coleta; não confia apenas em flags de elegibilidade vindas de outro arquivo.
- As métricas usam a interseção dos casos elegíveis entre **todos os braços fornecidos**, com a mesma observação. Reporta também pares fora da interseção, motivos sobrepostos de exclusão, exclusões únicas e ausências na união dos relatórios. A união não é o calendário completo da campanha: alvos omitidos por todos os braços não podem ser contados sem o manifesto correspondente.
- MAE, RMSE e viés reutilizam `domain.verification`, sem alterar esse módulo congelado. Ganho relativo de MAE é indefinido se a baseline tiver erro zero ou não houver pares; não há divisão artificial.
- Detecção diagnóstica de chuva alta usa 50 mm/dia da reference-v1: hits, misses, falsos alarmes, rejeições corretas, detecção, razão de falsos alarmes e taxa de falso positivo. Sem positivos observados, recall é indefinido. O limiar não se torna um novo critério científico aprovado.
- Estratificação por estação e dias após coleta, além do resumo agregado. O relatório preserva hashes das entradas e dos casos comuns. Não calcula intervalos de confiança, ranking de vencedores ou aprovação estatística.
- O fingerprint do manifesto agora inclui comparador e verificador numérico. Um manifesto do pipeline anterior deve ser refeito; não alterar silenciosamente sua identidade.

## D+7 e baseline automática

Quando um modelo tem D+7 e a baseline pública não, o estrato permanece visível com zero pares comuns e métrica indefinida. Isso resolve o tratamento técnico da ausência; **não define ainda um substituto científico para a baseline pública em D+7**. O controle desse horizonte continua pendente de decisão no desenho.

A inicialização desconhecida da baseline automática não é inferida a partir da coleta. O padrão do comparador exige uma inicialização informada anterior ao alvo; para uma análise operacional explícita por dias após coleta é necessário usar `require_run=False` ou a opção CLI correspondente. Esse modo não prova igualdade de antecedência de rodada entre os braços. A aprovação científica continua falsa em ambos.

## Uso offline

```powershell
python -m climaprev.tools.experimental_comparison --input baseline-pairs-v2.json --input candidate-pairs-v2.json --baseline operational-baseline --output comparison.json --allow-unknown-run
```

Os nomes são exemplos: fornecer relatórios v2 reais, já pareados no mesmo ponto e intervalo. Usar `--allow-unknown-run` somente quando a análise for explicitamente baseada em coleta, com a limitação de origem/rodada preservada. Não é autorização de campanha. Para diagnóstico retrospectivo, `--allow-retrospective` também precisa ser explícito; o padrão exclui coleta posterior ao alvo. Nenhum modo concede promoção ou aceita a independência dos dados.

O CLI lê apenas os arquivos indicados, usa o leitor limitado existente e grava resultado sem sobrescrever. Não coleta dados ou varre reservas automaticamente. Relatórios v1 são rejeitados por falta de metadados temporais; regenerar novas versões a partir de fontes autorizadas, preservando as anteriores.

## Validação e alcance

75 testes direcionados Docker aprovados, abrangendo comparador, entrada da baseline, pareamento, manifestos, coletores e arquivo. Mypy aprovado nos três módulos afetados e Ruff nos módulos/testes experimentais. Incluídos casos com resultado numérico conhecido, D+7 sem controle, zero eventos, baseline perfeita, intervalo inválido, origem observacional diferente, duplicatas, chuva negativa, retrospectiva explícita e CLI sem sobrescrita.

O incremento foi exercitado com fixtures sintéticas; **não foram calculados novos ganhos sobre dados reais ou reservados**. Último checkpoint integral backend e verificação da interface são os registros anteriores de 714 backend e 48 frontend; não foram reexecutados como suites completas nesta continuação. Novas mudanças sem commit/push ou CI remoto.

## Próximos trabalhos

Fechar o controle científico de D+7, tolerâncias/amostra/calendário, integrar o calendário planejado à cobertura global e desenvolver intervalos estatísticos conforme protocolo fechado. Pareamento de temperatura, vento/rajadas e umidade aguarda equivalência instrumental. Acionador recorrente permanece desativado. Teste auditivo e publicação do lote continuam pendentes.

[RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Implementação anterior](../contexto/RELATORIO-IMPLEMENTACAO-2026-10-26.md).
