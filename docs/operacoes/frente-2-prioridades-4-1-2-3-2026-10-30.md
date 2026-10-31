# Frente 2 — entregas na ordem 4 → 1 → 2 → 3

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Resultado de 30/10/2026

Implementadas quatro ferramentas de análise, sem modificar os módulos congelados da coleta ou a API pública. O calendário ativo foi validado novamente: seus fingerprints continuam válidos. A automação diária e a reposição até a cota permanecem com as condições aprovadas pelo usuário. A reference-v1 segue padrão.

## 4 — Relatório de encerramento do piloto

`experimental_pilot_report.py` lê o protocolo, calendário semente, todas as extensões, ledger e CSVs observacionais fornecidos explicitamente. Reutiliza a auditoria de capturas válidas e conserva as tentativas perdidas no denominador. Expõe:

- Capturas aceitas e saldo por estação/modelo; reposições aceitas fora das datas semente.
- Estados operacionais, reservas sem resolução e arquivos concluídos rejeitados pela auditoria.
- Dias observacionais devidos, pendentes ou incompletos, com horas esperadas/válidas e hash da fonte.
- Fim real da cauda D+7, considerando as datas efetivamente capturadas e os fusos das estações.
- Encerramento técnico somente quando cota e cauda observacional estiverem completas. Encerramento técnico não autoriza promoção nem demonstra precisão.

O CLI recusa calendário de outro protocolo e escreve somente em arquivo novo. Não coleta dados nem altera o ledger. É obrigatório fornecer todos os manifestos; omissões sem registro no ledger não podem ser descobertas automaticamente. Arquivo sem origem/contrato instrumental verificado não se torna cientificamente certificado pela cobertura.

Executado no piloto real em preparação: zero capturas de piloto, 210 jobs futuros, encerramento falso. O diagnóstico de preflight anterior não entrou na cota. Relatório completo local em `.report-work/analysis-priorities-2026-10-30/pilot-report-final.json`; resumo versionado em `docs/planejamento/reference-candidate-1/evidence/entrega-prioridades-2026-10-30.json`.

## 1 — Equivalência das variáveis secundárias

`experimental_measurement_review.py` acrescenta uma revisão explícita de ponto, altura do sensor acima do solo e representatividade declarada. Altitude da estação não é usada como altura do sensor. Informações ausentes e pontos/alturas divergentes aparecem como bloqueios separados das incompatibilidades de unidade, variável, período e semântica.

Contrato de vento com média nativa de dez minutos pode ser verificado quando os dois lados realmente declaram essa média e a mesma janela. Vento instantâneo continua incompatível. Não foi criada média a partir de instantâneos nem habilitado novo campo de provedor. Temperatura média horária e instantânea continuam distintas; umidade sem agregação esclarecida permanece inelegível para comparação instantânea.

Contextos são declarações de entrada, sem autenticação independente. Mesmo uma revisão declarada completa não dá aprovação científica. A conclusão instrumental real continua dependendo de documentação das estações/fontes e revisão de representatividade.

## 2 — Preparação estatística

`experimental_statistical_plan.py` entrega:

- Alocação prospectiva Bonferroni para uma família finita pré-definida. Com confiança familiar de 95% e sete declarações, a confiança marginal alocada é aproximadamente 99,2857%.
- Avaliação das declarações selecionadas com a confiança alocada, somente em desenvolvimento. Seleção/confirmacão reservadas são recusadas nessa função; não há escolha de melhor modelo ou bloco por resultado.
- Sensibilidade dos blocos e diagnóstico de segmentos, blocos completos do calendário e datas/casos de eventos. Nenhum desses contadores é declarado número de eventos meteorológicos independentes.

O [NIST descreve a alocação de confiança por Bonferroni](https://itl.nist.gov/div898/handbook/prc/section4/prc473.htm). Sua aplicação depende de intervalos marginais válidos. Ajustar a confiança de um bootstrap exploratório não prova cobertura simultânea ou suporte suficiente; esses estados continuam falsos nos resultados. Faltam validar método/bloco, suporte efetivo, poder e plano final antes da confirmação. Nenhum bloco foi selecionado automaticamente.

Plano prospectivo de sete declarações salvo em `familia-estatistica-preparada-2026-10-30.json`: MAE D+1 agregado e duas proteções de extremos por estação. Esse artefato é preparação metodológica; não modifica o protocolo congelado do piloto nem afirma pré-registro confirmatório concluído.

## 3 — Alternativas de refinamento

`experimental_forecast_variants.py` permite combinações de pesos fixos positivos que somam um, seguidas de escala e deslocamento explícitos. Exige mesma variável, unidade, janela e semântica nativa. Modelo/valor ausente produz alternativa incompleta; não redistribui pesos silenciosamente. Limites físicos aplicados são registrados, inclusive o corte de chuva negativa e a faixa de umidade. Temperaturas negativas permanecem válidas. Coeficientes inválidos/overflow são rejeitados.

Cada saída registra identidade dos parâmetros, hash dos dados de entrada e da implementação. Não há ajuste de pesos, ranking, calibração probabilística ou ligação ao endpoint público. A identidade reservada reference-v1 não pode nomear uma variante nova. Concordância entre fontes não vira probabilidade de acerto; combinações podem suavizar extremos e exigem avaliação independente.

Dois modelos de especificação foram preparados em `alternativas-preparadas-2026-10-30.json`: identidade GFS e combinação igual de GFS/IFS/ICON, apenas como alternativas experimentais. Nenhum desempenho foi calculado com dados reais; nenhum coeficiente de correção foi estimado. A abertura/avaliação dos conjuntos reais exige o escopo e os registros aplicáveis antes de desenvolvimento/seleção.

## Qualificação e pendências

29 testes novos aprovados, incluindo encerramento/cobertura com perda preservada, CSV incompleto, cauda futura, protocolo divergente, contratos instrumentais, multiplicidade, suporte temporal, pesos, ausência, correção e proteção da identidade v1. Ruff integral e mypy dos quatro módulos aprovados. A qualificação integral remota deve ser conferida no próprio SHA do incremento.

Permanecem pendentes: executar a coleta agendada e fechar sua cauda observacional; comprovar contratos instrumentais reais; validar o método estatístico com dados elegíveis; ajustar/selecionar variantes em partições próprias; revisar o calendário científico após reposições; congelar e confirmar a candidata; obter aceite e qualificar a ativação real. Acessibilidade auditiva e distribuição/comercial continuam separadas. Não houve coleta extra, fitting, nova leitura de resultados reservados ou promoção nesta entrega.
