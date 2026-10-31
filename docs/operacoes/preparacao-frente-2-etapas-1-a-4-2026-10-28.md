# Frente 2 — Fechamento da preparação das etapas 1 a 4

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Data: 28/10/2026. O usuário autorizou continuar as etapas de preparação: verificar estações, definir calendário/rodadas, separar dados e fundamentar critérios, com aceite técnico delegado. Preparação não equivale a executar 14 dias de piloto nem a demonstrar qualidade científica.

## 1. Estações: metadados verificados e limites identificados

Consulta ao [catálogo oficial INMET](https://apitempo.inmet.gov.br/estacoes/T) em 28/10 registrou A201, A001 e A801 como operantes. O resumo preserva fonte, momento de consulta, hashes e coordenadas. Situação cadastral operante não comprova fluxo recente ou precisão instrumental.

| Estação | Chuva: dias completos em 2024 / 366 | Dias com pelo menos 50 mm | Situação atual verificada |
|---|---|---|---|
| A201 Belém | 365 | 8 | Operante no catálogo; coordenadas atuais diferem do CSV histórico além da tolerância do pareamento |
| A001 Brasília | 342 | 2 | Operante no catálogo; coordenadas coincidem com o histórico consultado |
| A801 Porto Alegre | 349 | 9 | Operante no catálogo; coordenadas coincidem com o histórico consultado |

São diagnósticos de observações de 2024 já conhecidas, apenas para desenvolvimento. Não são pares de previsão, contagem de eventos independentes ou validação de dados de 2026. Dias incompletos, inclusive o limite final do arquivo, permanecem no denominador.

Belém tem latitude histórica -1,411228 e atual -1,41111111; longitude histórica -48,439512 e atual -48,43944444. Não foi inferida mudança física da estação: a causa pode ser revisão cadastral e não foi demonstrada. Os dados históricos foram preservados; novas observações precisam de metadados versionados e reconciliação explícita antes do pareamento. Não aumentar a tolerância silenciosamente.

Os acessos de observações recentes, tanto por instante como por estação no período 21–27/10, retornaram HTTP 204 sem conteúdo. Isso descreve as consultas efetuadas, não prova ausência de medições em todo o INMET. **Qualidade observacional atual ainda não está validada e impede declarar o conjunto pronto para confirmação.** Próxima ação operacional: obter uma fonte oficial recente com dados e unidades verificáveis, por CSV público disponível ou acesso documentado, e reconciliá-la ao catálogo.

## 2. Calendário e rodadas definidos, sem ativação

- Piloto técnico preparado: **29/10 a 11/11/2026**, uma coleta diária às **18 UTC / 15h de Brasília**.
- Três estações e cinco braços: GFS, IFS, ICON, MET Norway e baseline operacional; **15 jobs/dia, 210 jobs planejados**. Não são chamadas já realizadas nem garantia de faturamento por requisição lógica.
- Modelos explícitos: solicitar inicialização **00 UTC** da mesma data. O manifesto agora congela a rodada e o runner a repassa ao coletor, sem trocar silenciosamente pela mais recente.
- MET Norway e baseline mantêm inicialização desconhecida quando não comprovada. As comparações operacionais usam a disponibilidade na mesma decisão planejada, não alegação de igualdade de idade dos modelos. Comparação controlada por rodada é secundária e exige dados elegíveis.
- Calendário e manifestos estão **desativados**; não há agendador instalado. Slot vencido não será preenchido depois com dado novo; perda de calendário exige novo registro antes de executar.

O preflight pontual em Belém obteve HTTP 200 para GFS/IFS/ICON da rodada 28/10 às 00 UTC, consultada aproximadamente às 16h30 UTC. Campos e unidades foram normalizados: GFS/IFS cobriram chuva diária D+1/D+3/D+7; ICON não completou o dia local D+7. Isso não verifica os outros pontos nem garante disponibilidade futura às 18 UTC.

A [documentação do provedor](https://open-meteo.com/en/docs/model-updates) distingue inicialização, conversão e disponibilidade, e informa consistência eventual entre servidores. O horário escolhido é um plano conservador de coleta; não uma comprovação de primeira publicação.

Calendário completo local ignorado pelo Git: `.report-work/front2-readiness-2026-10-28/pilot-calendar.disabled.json`. [Evidência resumida e hashes](../planejamento/reference-candidate-1/evidence/preparacao-frente-2-2026-10-28.json). Regerar deliberadamente um novo calendário se a implementação/pipeline mudar antes da execução, preservando a identidade do anterior.

## 3. Partições registradas com proteção contra contaminação

[Registro temporal e allowlist](../planejamento/reference-candidate-1/particoes-temporais-2026-10-28.json).

| Partição / marco | Calendário de planejamento | Regra |
|---|---|---|
| Desenvolvimento | Alvos até 18/11/2026; materiais conhecidos a partir de 2024 | Apenas fontes explicitamente permitidas; a janela não autoriza abrir qualquer arquivo de 2025 ou outro material reservado |
| Congelamento do conjunto de alternativas | Até 25/11/2026, 23 UTC | Antes da primeira emissão D+7 para seleção, em 26/11 às 00 UTC |
| Seleção | Alvos de 03/12 a 31/12/2026 | Sem usar confirmação para escolher ou reajustar alternativas |
| Congelamento final da candidata e protocolo | Até 07/01/2027, 23 UTC | Antes da primeira emissão confirmatória D+7, em 08/01 às 00 UTC |
| Confirmação | Alvos de 15/01/2027 a 14/01/2028 | 12 meses planejados; só executar com pré-condições satisfeitas |

Embargo mínimo de sete dias, levando em conta também a primeira emissão e o maior horizonte, além dos dias dos alvos. Separação aritmética não prova independência meteorológica. O validador rejeita sobreposição, embargo insuficiente e congelamento posterior à primeira emissão de confirmação.

Datas são condicionais, não declarações de congelamento já realizado. Se o piloto, os dados ou a candidata não estiverem prontos, invalidar esse calendário e pré-registrar outro antes de novos resultados, sem alterar retrospectivamente a reserva por desempenho. Não esperar até consultar resultados para decidir a partição.

A allowlist inicial inclui somente os três CSVs de 2024 já conhecidos e o replay exploratório de Belém já exercitado, com hashes. Os demais arquivos existentes ficam em quarentena lógica no manifesto, sem leitura de outcomes ou reclassificação como teste independente. Não houve movimentação ou bloqueio de arquivos no sistema operacional; a allowlist precisa orientar a ingestão futura.

## 4. Critérios conservadores preparados por delegação

[Configuração e justificativas](../planejamento/reference-candidate-1/criterios-preparados-2026-10-28.json). Esses parâmetros são decisões prospectivas de desenho, não limiares cientificamente validados por dados novos.

- Meta principal: ganho de pelo menos **5% no MAE de chuva diária D+1**, com intervalo pareado favorável à candidata e leitura de cobertura por estação.
- Cobertura comum mínima de **90% dos alvos planejados por estação**, como regra operacional de completude. Em 365 dias são ao menos 329 pares por estação; isso não significa 329 eventos independentes.
- **Sem tolerância automática à piora dos extremos:** limite inferior do intervalo da diferença de detecção deve ser pelo menos zero; limite superior da diferença da razão de falsos alarmes deve ser no máximo zero. Trata-se de proteção conservadora, que pode levar a resultado inconclusivo ou a critérios não atendidos.
- Confiança reportada de **95%** e largura máxima de **0,10** para intervalos das diferenças de detecção/falsos alarmes, como requisito de precisão prospectivo. A escolha não demonstra que os dados disponíveis atendam à precisão.
- Sem eventos observados ou previstos, ou sem intervalos suficientemente informativos, resultado inconclusivo. Um evento no contrato é apenas piso de computabilidade; não representa suporte científico suficiente.
- Ganho absoluto em mm/dia deve ser reportado. A proposta de **0,5 mm/dia** permanece análise de sensibilidade: não foi transformada em margem física validada. As tolerâncias anteriores de cinco pontos percentuais não serão autorização automática para degradar extremos.
- Uma comparação principal agregada em D+1; estratos, outros modelos/horizontes e variáveis secundárias são exploratórios. Não usá-los para escolher retrospectivamente uma alegação confirmatória favorável. Os critérios de promoção precisam ser atendidos em conjunto, inclusive proteções por estação.
- Método de incerteza deve preservar pareamento e agrupamento temporal por data. Comparar blocos de 7/14/28 dias em desenvolvimento e congelar a escolha antes da confirmação. **Comprimento final ainda depende do diagnóstico dos erros**; o bootstrap/avaliação independente será implementado na etapa própria, não declarado pronto agora.

A [orientação NIST](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbici.htm) alerta para aproximações inadequadas em amostras binomiais pequenas. A [pesquisa de verificação de previsões](https://journals.ametsoc.org/doi/10.1175/MWR-D-17-0295.1) mostra a importância da dependência temporal; não tratamos dias como amostras IID. Essas referências sustentam a cautela metodológica, não prescrevem os valores operacionais de 90% ou largura 0,10 adotados aqui.

O avaliador diagnóstico ganhou exigência opcional de suporte de eventos previstos e precisão dos intervalos. Continua sem calcular intervalos ou autenticar metodologia/independência declaradas, e mantém promoção desautorizada em qualquer resultado.

## Resultado e pendências que não podem ser declaradas concluídas

As entregas de preparação das quatro etapas foram produzidas: catálogo reconciliado, diagnóstico histórico, rodada no manifesto, calendário desativado, partições com allowlist e critérios documentados/testáveis. Nenhum desempenho novo da candidate-1 foi medido.

Permanecem bloqueios empíricos: **obter observações atuais válidas, reconciliar a versão de Belém, medir suporte efetivo e calibrar o bloco temporal antes do teste confirmatório**. Não são novos pedidos rotineiros de aceite; são verificações dependentes de dados. Não declarar a campanha cientificamente pronta enquanto faltarem.

Sem ativação de rotina, fitting, leitura de novos outcomes reservados, promoção, merge ou push nesta rodada. A reference-v1 permanece ativa.

## Qualificação final

826 testes backend completos aprovados em 63,40 s, warnings como erros, com Redis de testes isolado; mypy Linux em 86 módulos e Ruff aprovados. Cenários cobrem calendário desativado, rodada congelada encaminhada ao coletor, reconciliação de coordenadas, embargo também na emissão D+7, congelamento anterior ao teste, precisão dos intervalos e suporte de eventos previstos. Frontend sem mudança nesta rodada. Arquivos históricos preservados; nenhum novo ganho de precisão calculado. Incremento local sem commit/push ou qualificação remota própria.
