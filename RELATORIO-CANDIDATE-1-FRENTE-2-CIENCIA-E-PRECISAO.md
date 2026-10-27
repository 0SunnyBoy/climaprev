# Candidate-1 — Frente 2: Ciência, precisão e integração

Atualizado em 27/10/2026. Este relatório distribui responsabilidades de implementação; os parâmetros finais continuam em revisão por escolha expressa do usuário.

## Objetivo

Definir e executar uma avaliação que permita desenvolver o refinamento da candidate-1 e decidir, com evidência independente, se ela pode substituir a reference-v1. Melhorar a previsão meteorológica e melhorar a classificação de risco são resultados distintos e precisam de verificações próprias.

## Implementações sob responsabilidade desta frente

| ID | Implementação | Estado atual | Entrega necessária para conclusão |
|---|---|---|---|
| F2-01 | Fechar protocolo, localidades e calendário | Direção aprovada; parâmetros finais em revisão | Definir estações, datas, duração, suporte e separação entre desenvolvimento, validação de seleção e confirmação. Registrar aceite do usuário antes de iniciar a campanha correspondente |
| F2-02 | Definir equivalência instrumental e elegibilidade | Chuva possui pareamento exploratório; demais variáveis pendentes | Especificar alvos, intervalos, unidades, qualidade e representatividade da estação frente à grade. Não equiparar automaticamente temperatura instantânea a extrema horária nem vento sustentado a rajada |
| F2-03 | Definir o controle científico de D+7 | Pendente; ausência da baseline já aparece no comparador | Aprovar comparador e interpretação para D+7. A baseline pública atual cobre hoje UTC até +6; não inventar seu valor em D+7. Comparar outros modelos entre si não demonstra ganho contra a baseline ausente |
| F2-04 | Fixar métricas e critérios de aprovação | Direção inicial aceita; detalhes ainda propostos | Chuva diária D+1 como objetivo inicial e meta direcional de redução de pelo menos 5% no MAE. Fechar relevância física, cobertura mínima, proteção dos extremos, suporte e critérios próprios das demais variáveis |
| F2-05 | Completar o comparador de modelos e baseline | Comparador exploratório de chuva implementado | Ampliar a análise para demais variáveis e horizontes elegíveis; manter casos comuns, exclusões, cobertura por braço e limitações explícitas. Valores ausentes não viram zero |
| F2-06 | Implementar incerteza e avaliação independente | Pendente; comparador atual fornece estimativas pontuais | Fechar e implementar método pareado, dependência temporal, agrupamento entre locais, estratos e comparações múltiplas quando aplicável. Verificar suporte e registrar resultados inconclusivos sem promoção |
| F2-07 | Desenvolver correções e combinações da candidata | Pendente | Testar alternativas somente em desenvolvimento e seleção, comparando com baseline e modelos individuais. Congelar parâmetros e versão antes do teste confirmatório; concordância entre fontes não vira probabilidade calibrada automaticamente |
| F2-08 | Executar confirmação e obter aceite final | Não iniciada; sem superioridade comprovada | Avaliar a candidata congelada nos dados independentes do calendário aprovado, incluindo extremos e indisponibilidade. Produzir relatório de ganho, regressões e limitações para decisão do usuário |
| F2-09 | Integrar a candidata qualificada à aplicação | Condicionada à evidência e ao aceite | Versionar modelo/política e proveniência; tratar divergências e dados parciais; validar contrato, latência, regressão e retorno à versão anterior. Preservar distinção entre risco calculado e avisos oficiais |

## O que já existe

O módulo `src/climaprev/tools/experimental_comparison.py` compara chuva em casos elegíveis comuns, com MAE, RMSE, viés, ganho relativo quando definido e diagnóstico de detecção/falsos alarmes. Expõe exclusões e estratos por estação e antecedência em dias de coleta. Essa etiqueta não comprova igualdade de antecedência da rodada meteorológica.

O comparador é exploratório: não fornece intervalos de incerteza ou aprovação automática. Os coletores e a auditoria operacional da Frente 1 apoiam a avaliação, mas não constituem evidência de ganho de precisão.

## Decisões ainda não aprovadas

- Estações A201 Belém, A001 Brasília e A801 Porto Alegre como conjunto inicial.
- Piloto técnico de 14 dias e confirmação de 12 meses após congelar o desenho e a candidata. São propostas; o piloto não amplia o horizonte público e um ano não garante suporte suficiente para extremos.
- Margem física de 0,5 mm/dia de MAE, tolerâncias de cinco pontos percentuais para detecção/falsos alarmes e demais critérios quantitativos.
- Intervalo de 95%, blocos inicialmente propostos de sete dias, cobertura mínima, limiares dos estratos e calendário exato.
- Comparador e interpretação final de D+7.

Essas propostas não devem ser aplicadas como regras aprovadas. Os valores de chuva também não se transferem automaticamente para temperatura, vento ou umidade.

## Sequência de execução

1. Revisar os parâmetros com o usuário e especificar o que o piloto precisa demonstrar.
2. Entregar à Frente 1 os contratos científicos de observações, alvos e elegibilidade.
3. Analisar a viabilidade operacional do piloto autorizado e fechar os parâmetros pendentes sem usar resultados reservados para escolher critérios.
4. Completar comparador, cobertura científica e métodos de incerteza.
5. Desenvolver e selecionar refinamentos em partições próprias.
6. Congelar candidata, desenho, versões e calendário antes da confirmação.
7. Executar avaliação independente e apresentar resultados para aceite.
8. Integrar a versão aprovada e validar comportamento da aplicação antes de qualquer promoção.

## Dependências e fronteira de responsabilidade

A Frente 1 entrega fontes, proveniência, coletas e observações pareadas com cobertura explícita. A Frente 2 estabelece como esses dados podem ser comparados e se sustentam uma conclusão de qualidade. Falhas identificadas na avaliação retornam à Frente 1 para correção, preservando versões e registros anteriores.

As frentes podem avançar em paralelo na preparação. O teste confirmatório exige desenho aprovado e candidata congelada. Nenhum resultado reservado deve orientar ajuste de pesos ou escolha posterior do período de avaliação.

## Critério de conclusão

Protocolo aprovado, avaliação independente reproduzível, desempenho e proteção dos extremos demonstrados conforme critérios aceitos, decisão final registrada e integração validada se houver aprovação. Se a evidência for insuficiente ou desfavorável, a entrega é um relatório conclusivo sobre essa limitação; a reference-v1 permanece ativa.

## Referências

- [Frente 1 — Dados e integrações](RELATORIO-CANDIDATE-1-FRENTE-1-DADOS-E-INTEGRACOES.md).
- [RDP geral](RELATORIO-PENDENCIAS-2026-10-20.md).
- [Direção aprovada e seus limites](docs/planejamento/reference-candidate-1/aprovacao-direcao-2026-10-23.md).
- [Parâmetros propostos](docs/planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md).
- [Revisão solicitada pelo usuário](docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md).
- [Comparador exploratório de chuva](docs/operacoes/comparacao-experimental-2026-10-26.md).
