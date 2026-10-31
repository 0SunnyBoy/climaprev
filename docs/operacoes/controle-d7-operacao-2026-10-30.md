# Operação do controle D+7 separado

## Estado

Infraestrutura implementada, **não ativada**. Não alterar a automação `piloto-t-cnico-climaprev`. [Resultado e qualificação](refatoracao-controle-d7-2026-10-30.md) · [Especificação original](../planejamento/reference-candidate-1/controle-d7-prospectivo-2026-10-30.md).

## Planejamento próprio

Usar um envelope `climaprev-experiment-protocol-v1` conforme `validate_protocol`, com identidade/code_version próprios, catálogo de estações verificado, lista explícita de slots futuros às 18 UTC, partições de desenvolvimento/validação/teste não sobrepostas e hash calculado com `digest(protocol)`. Não copiar slots ou partições condicionais do piloto como se estivessem aprovados para D+7.

Campos específicos:

```json
{
  "models": ["operational-baseline"],
  "horizons": [7],
  "variables": [{"name": "precipitation_mm", "unit": "mm", "semantics": "previous_hour_sum", "aggregation": "sum"}],
  "slot_window_minutes": 30,
  "provider_daily_call_limit": 30,
  "criteria": {
    "control_scope": "adapter_policy_d7_epoch_two_day_transport_v1",
    "execution_scope": "secondary_exploratory_only"
  }
}
```

Este trecho é um contrato parcial, não um protocolo executável ou aprovação. Todos os alvos D+7 precisam pertencer a desenvolvimento; o coletor não abre seleção/confirmação. Modelo completo sintético, exclusivamente para compreender o contrato: `tests/unit/tools/test_experimental_d7_control.py`.

Com um protocolo próprio validado, gerar calendário **desativado**:

```powershell
$env:PYTHONPATH = 'src'
.venv/Scripts/python.exe -m climaprev.tools.experimental_d7_control plan --protocol .report-work/d7-control/protocol.json --output .report-work/d7-control/calendar.disabled.json
```

Os arquivos de entrada precisam existir, e a saída precisa ser nova. O comando não faz HTTP. Habilitar um calendário exige `--enable --approval CAMINHO_E1_PROPRIO`; a execução volta a verificar esse E1. Registros são rastreabilidade local, não assinatura/autenticação humana criptográfica. Não criar aprovação fictícia.

## Execução explícita após prontidão

Só executar após completar a quota de previsões do piloto e passar todas as suas datas de manifestos, sem reservas sem resolução. Isso é deliberadamente mais conservador que duas rotinas concorrentes. Fornecer o histórico completo: manifestos originais da semente e todas as extensões, inclusive falhas. O auditor não pode descobrir extensões omitidas que nunca chegaram ao ledger.

O CLI `run` exige protocolo/calendário D+7, E1 próprio, protocolo do piloto, `--pilot-manifest` repetido para cada manifesto, ledger original somente para leitura, ledger D+7 e diretório de arquivos próprios, mais uma saída de relatório nova. Não passar o envelope do calendário semente como se fosse um manifesto individual; seus manifestos estão em `calendar.manifests`.

Para usar diretamente o calendário semente e suas extensões sem exportar os manifestos, a API Python `run_control_calendar` aceita a lista extraída de `seed["calendar"]["manifests"]` somada às extensões. Validar o calendário semente com `validate_target_calendar` e confirmar o mesmo protocolo do piloto antes de montar essa lista. A ordem de fornecimento não dispensa incluir todos os manifestos.

Workspace sugerido: `.report-work/d7-control/`, fora de `.report-work/inmet-browser-2026-10-30/`. Não usar nova pasta dentro do workspace do piloto: o executor a rejeita. Falhas e reservas não são reabertas; uma nova tentativa exige nova data futura planejada.

## Interpretação dos arquivos

Cada captura possui JSON identificado por conteúdo e um arquivo `.body` com o corpo HTTP descomprimido original. `load_control_archive` confere os hashes. O recorte diário normalizado e o risco derivado são separados da resposta original. Uma chamada busca dois dias em epoch/fuso explícito para incluir o fechamento da última hora do alvo; isso é uma nova versão de transporte do controle, não o antigo coletor v5.

`rain_eligible_exploratory` exige chuva horária completa, total diário disponível e horário de captura válido. Isso não aprova instrumentos, representatividade, suficiência de eventos, significância ou promoção. Captura incompleta fica `ineligible`; falha continua registrada. Não há reposição automática D+7 nesta entrega, nem fitting ou integração com a API pública.

[Terceira revisão concluída, achados e verificações](terceira-revisao-refatoracao-2026-10-30.md).
