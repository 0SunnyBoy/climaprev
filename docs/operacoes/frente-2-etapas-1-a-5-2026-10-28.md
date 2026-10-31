# Frente 2 — Publicação e integração das etapas 1 a 5

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Data: 28/10/2026. Escopo: publicar o lote local, revisar acesso observacional e contratos, requalificar o piloto e ligar coleta/observação/cobertura/relatórios. Não inclui calcular incerteza, ajustar candidata ou iniciar confirmação.

## 1. Consolidação e publicação

Lote de 845 testes publicado na develop em `baa3465`, com CI e Security gates aprovados. O incremento seguinte desta rodada corrige a interpretação instrumental e integra os relatórios; precisa de sua própria qualificação remota. O resultado de qualquer revisão deve ser consultado pelo SHA exato, não herdado de `baa3465`.

Um plano local de extração de API, criado fora do escopo desta rodada, foi preservado sem publicação. A ausência de inclusão desse arquivo não é perda de alterações.

## 2. Acesso observacional

Índice oficial reconsultado: publicação anual de 2026 ainda termina em 30/09. Os três CSVs já obtidos são válidos para essa publicação e estão isolados como desenvolvimento. Não satisfazem a janela de outubro necessária para liberar o piloto pareado.

A interface recente usa fluxo protegido por reCAPTCHA. Não houve solução de CAPTCHA, reutilização de tokens ou bypass. Sem uma fonte recente obtida por acesso legítimo e com campos verificados, essa parte permanece bloqueada. Não interpretar respostas antigas 204 como ausência real de medições em todas as fontes do provedor.

## 3. Contratos instrumentais

A [revisão oficial dos contratos](../planejamento/reference-candidate-1/contratos-instrumentais-verificados-2026-10-28.md) identificou que a temperatura horária automática é média, não instantânea. O parser foi corrigido e o comparador passou a bloquear essa equivalência. A umidade conserva intervalo não resolvido, sem presumir instantaneidade; vento médio de dez minutos não equivale à velocidade prevista instantânea.

Rajada e chuva permanecem diagnósticos por intervalos próprios. Altura, calibração e representatividade local não foram certificadas pela documentação disponível. Os arquivos históricos congelados permaneceram preservados.

## 4. Requalificação do piloto

Calendário v2 desativado preparado para 29/10–11/11, às 18 UTC, cinco braços/três estações. Identidade de pipeline atualizada, preservando calendários anteriores. Fonte e slot de cada captura do preflight foram verificados offline; nenhuma chamada meteorológica adicional foi necessária para reprocessar esses arquivos.

`qualify_primary_pilot` verifica integridade/atualidade dos manifestos, cinco braços em cada ponto, estações operantes, revisão atual do relatório, observações de chuva na janela recente e previsões D+1 disponíveis. Retorna prontidão, mas não altera calendários nem instala rotina.

Resultado real: **previsões D+1 disponíveis nos cinco braços/três locais; chuva observada recente com cobertura zero nas fontes de setembro**. Os três bloqueios registrados são observações recentes incompletas de A201/A001/A801. Piloto não ativado. A inadequação de variáveis secundárias é tratada separadamente, sem exigir que as observações de amanhã já estejam disponíveis hoje.

Se o calendário vencer ou o pipeline mudar antes da liberação, preparar uma nova versão deliberadamente. Não substituir slots perdidos por dados posteriores nem alterar hashes antigos para habilitar execução.

## 5. Avaliação integrada

Novo `tools/experimental_evaluation.py`, utilizável por função ou CLI offline:

- Lê somente arquivos explicitamente fornecidos; sem glob, coleta, ajuste ou promoção.
- Verifica nome por conteúdo, hash do payload, limites de tamanho, metadados, identidade de modelo/rodada, coordenadas e slot de coleta.
- Liga cada captura à versão do CSV da estação e aos horizontes D+1/D+3/D+7.
- Integra o comparador diário de chuva com baseline operacional e os relatórios horários em referência experimental identificada.
- A baseline diária não é transformada em série horária. Ausência de baseline D+7 continua explícita.
- Mantém o denominador planejado mesmo sem arquivos ou braços; registra a cobertura, exclusões e disponibilidade de cada fonte.
- Temperatura instantânea e umidade não recebem scores quando a observação não tem semântica equivalente. Rajada usa somente modelos com essa capacidade normalizada, declarada antes da comparação.
- Registra identidade dos arquivos, hash do CSV e versões de pipeline da avaliação. Integridade não autentica independentemente a declaração do provedor.
- Escrita exclusiva do resultado, sem sobrescrita de relatórios.

Exemplo de comando, com caminhos explícitos do operador:

```powershell
python -m climaprev.tools.experimental_evaluation `
  --station-csv "CAMINHO_DO_CSV" `
  --station A201 --timezone America/Belem `
  --slot 2026-10-28T16:57:58+00:00 `
  --archive "operational-baseline=CAMINHO_BASELINE" `
  --archive "gfs_global=CAMINHO_GFS" `
  --archive "ecmwf_ifs025=CAMINHO_IFS" `
  --archive "icon_global=CAMINHO_ICON" `
  --archive "met-norway=CAMINHO_MET" `
  --output "CAMINHO_NOVO_DO_RESULTADO"
```

Substituir os placeholders e usar o slot que corresponda aos arquivos reais. Os modelos e seus arquivos são declarados explicitamente, sem descoberta automática de outros conjuntos.

Na execução real das três estações, o pipeline integrou as quinze capturas existentes e encontrou zero pares comuns para os alvos de outubro/novembro nas observações encerradas em setembro. Isso aparece como falta de cobertura, não MAE zero, ausência de risco ou precisão perfeita. Nenhum ganho real da candidata foi calculado.

[Evidência resumida da integração](../planejamento/reference-candidate-1/evidence/integracao-por-estacao-2026-10-28.json). Relatórios completos e calendário v2 estão em `.report-work/front2-integrated-2026-10-28/`, isolados do Git e das reservas existentes.

## Resultado da rodada

Publicação inicial entregue; contratos corrigidos; relatório integrado e qualificação do piloto implementados. Acesso recente e liberação do piloto continuam condicionados à fonte observacional legítima. Não avançar para ajuste ou confirmação com ausência de dados ou contratos incompatíveis.

Sem modificação da API pública, do frontend ou da reference-v1. A qualificação de código não demonstra superioridade meteorológica ou prontidão para produção.

## Qualificação local

858 testes backend completos aprovados em 66,83 s, warnings como erros, com Redis de testes isolado; mypy Linux em 89 módulos e Ruff aprovados. Testes de CLI verificam integração explícita e recusa de sobrescrita; contratos verificam bloqueio de média versus instantâneo, e a prontidão exige observação recente/previsão/código compatíveis sem ativar rotina. O resultado remoto deve ser consultado no commit desta publicação, não no anterior.
