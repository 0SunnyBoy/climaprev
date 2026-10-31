# Integração local de develop2 — 30/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Origem e preservação

Branch de destino: `develop` local. Origem: `origin/develop2` em `9fd99b7fd40b69a750d65175e26bbd7a4495bd00`. A base publicada da develop era `315dd2b`. O trabalho local da frente 2 foi registrado primeiro em `bd7fbe3`, preservando análise de incerteza, calendário planejado, sensibilidade de blocos e documentos. O arquivo externo `docs/contexto/PLANO-EXTRACAO-CLIMAPREV-API.md` permanece fora do lote.

## Resultado da revisão

A develop2 entrega infraestrutura experimental de protocolo/partições, rastreabilidade, capacidades das fontes, medição, campanha limitada, cobertura, comparação multivariável, incerteza, relatório reproduzível, registro/seleção de estratégias e adaptador operacional explícito. Seu próprio relatório de encerramento distingue testes sintéticos de validação científica real. O merge incorpora a preparação técnica; não comprova melhora de previsão.

O comportamento padrão continua Open-Meteo/reference-v1, sem bundle de candidata configurado. A seleção explícita exige os artefatos e registros verificados pelo mecanismo recebido; não foi configurada nesta integração. Não houve coleta real, ajuste, acesso a resultados reservados, ativação do piloto, promoção, deploy, alteração da main ou push.

## Conciliação dos conflitos

- `experimental_campaign.py`: preservados todos os fingerprints locais e acrescentado o contrato de protocolo; conciliados rodada explícita e janela configurável do slot. Corrigida referência a parâmetro ausente após a junção automática.
- `experimental_observations.py`: preservadas as duas interfaces de observações, incluindo a qualificação local e o parser multivariável da origem. Ambas mantêm temperatura horária como média anterior, sem transformá-la em instantânea.
- `experimental_pairing.py`: preservada a verificação local de equivalência da chuva e incorporados os pareamentos, calendário e metadados da origem.
- Testes de incerteza: mantidos os dois conjuntos. O conjunto multivariável da origem passou para `test_experimental_study_uncertainty.py`, preservando `test_experimental_uncertainty.py` da análise local.
- `experimental_comparison.py`: junção automática revisada, mantendo a exposição opcional de pares locais e os recursos multivariáveis da origem.

## Verificação

Ruff integral de `src` e `tests` aprovado; mypy local dos cinco módulos conciliados aprovado. Frontend verificado com Node.js 22.23.2 isolado: 56 testes, lint e build aprovados; instalação pelo lockfile informou zero vulnerabilidades. Regressão backend Linux integral aprovada: **1.099 testes**, com warnings como erros, em 151,85 segundos. Mypy integral Linux aprovado em **93 módulos**. Resultado combinado qualificado localmente; sem CI remoto próprio porque não houve push.

## Pendências após a integração

Reconciliar o desenho científico final com os artefatos executáveis recebidos, definir multiplicidade/suporte/blocos com dados elegíveis, obter observações atuais, concluir equivalência instrumental, executar piloto e desenvolver/confirmar a candidata em partições próprias. O calendário desativado iniciado em 29/10 não deve ser preenchido retroativamente; antes de ativação real, revisar e versionar novo calendário, protocolo e hashes do pipeline combinado. Os ensaios sintéticos não satisfazem essas condições.

Os checkpoints anteriores da frente 2 sobre ausência de infraestrutura de seleção/integração são históricos: parte dessa infraestrutura chegou pela develop2. A avaliação empírica e o aceite de promoção continuam pendentes. Nenhuma branch remota será atualizada por este merge local.
