# Preparação do piloto — etapas 1 a 6, 30/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Resultado

Executada a sequência autorizada até a verificação de prontidão. O resultado é **não pronto**: faltam observações recentes verificadas e preflight atual. O piloto permanece desativado; nenhuma campanha longa, fitting ou promoção foi iniciada. Reference-v1 permanece padrão.

| Etapa | Entrega e estado |
|---|---|
| 1 — publicação e CI | Merge `cab7d8c79dca8756eedb6fccea27fd8a06796097` publicado na develop. [CI](https://github.com/0SunnyBoy/climaprev/actions/runs/41081566586) e [Security gates](https://github.com/0SunnyBoy/climaprev/actions/runs/41081566583) concluídos com sucesso nesse SHA. O incremento de preparação deste documento requer os workflows do seu próprio commit antes de ser considerado remotamente qualificado. |
| 2 — consolidação | Protocolo executável novo com hashes do plano de critérios e partições; validado pelo contrato da develop2. Tradução explícita: development/selection/confirmation correspondem a adjustment/validation/test do runner. Não foram emitidos registros E1/E2/E3. |
| 3 — estatística | Critérios prospectivos e fronteira confirmatória documentados. Meta pontual de 5%, cobertura por calendário, proteção dos extremos, limites das taxas, um objetivo primário e secundários exploratórios. Bloco final, suporte efetivo e validade conjunta ainda dependem de dados; não foram fabricados. |
| 4 — fontes e medições | Catálogo oficial e glossário revalidados. Cinco braços, dois provedores de acesso, ECMWF duplicado explicitamente entre IFS e MET. Chuva primária; variáveis sem contrato equivalente continuam bloqueadas. Termos de uso não comercial da API gratuita Open-Meteo e identificação/atribuição de MET registrados. |
| 5 — observações recentes | GETs públicos de 23–29/10 retornaram 204 nas três estações. Catálogo responde 200 e marca as três operantes; índice anual ainda até setembro. Não foi obtida nova observação contemporânea; interface responder 200 não comprova disponibilidade dos dados. |
| 6 — calendário e prontidão | Novo calendário completo, desativado, de 31/10 a 13/11 às 18 UTC/15h Brasília: 210 jobs e 630 alvos até 20/11. Verificador executado com relatórios reavaliados offline; retorna bloqueios de cobertura, janela observacional antiga e preflight de previsão antigo nas três estações. |

## Correção de prontidão

O gate anterior verificava cobertura/versões, mas não a idade do preflight. Agora exige `slot_utc` e `checked_at` válidos e ordenados até o relógio de verificação, com idade máxima de 24 horas. É uma regra operacional prospectiva desta preparação, não prova de equivalência da inicialização ou padrão científico universal. Testes cobrem captura antiga, avaliação futura e relógio ausente.

O fingerprint de campanha passou a incluir `experimental_preparation.py`. Manifestos e hashes antigos permanecem históricos; não editá-los para forçar aceitação. Antes da execução, gerar/revisar o calendário no runtime de destino com o código publicado. Os hashes de arquivos brutos do runtime local podem diferir de outro checkout por finais de linha; isso deve bloquear, não autorizar silenciosamente.

## Evidências e reprodução

- [Protocolo e interpretação científica](../planejamento/reference-candidate-1/protocolo-consolidado-2026-10-30.md).
- [Envelope executável](../planejamento/reference-candidate-1/protocolo-consolidado-2026-10-30.json).
- [Critérios](../planejamento/reference-candidate-1/criterios-consolidados-2026-10-30.json) e [partições](../planejamento/reference-candidate-1/particoes-temporais-2026-10-30.json).
- [Prontidão, horários e hashes](../planejamento/reference-candidate-1/evidence/prontidao-piloto-2026-10-30.json).
- [Acessos oficiais com status e hashes](../planejamento/reference-candidate-1/evidence/acesso-inmet-2026-10-30.json).

Os arquivos completos do calendário e os relatórios por estação estão em `.report-work/preparacao-piloto-2026-10-30/`, fora do Git; identidades e contagens estão no resumo versionado. Para regenerar apenas o calendário desativado, sem HTTP ou observações:

```python
import json
from pathlib import Path
from climaprev.tools.experimental_campaign import build_target_calendar, validate_target_calendar

protocol = json.loads(Path("docs/planejamento/reference-candidate-1/protocolo-consolidado-2026-10-30.json").read_text(encoding="utf-8"))
calendar = build_target_calendar(protocol, enabled=False, approvals=[])
validate_target_calendar(calendar)
with Path("pilot-calendar.disabled.json").open("x", encoding="utf-8") as output:
    json.dump(calendar, output, ensure_ascii=False, indent=2)
```

Não executar o calendário gerado automaticamente nem reutilizar um slot vencido. A janela recente concluída, calculada separadamente, é 23/10 03 UTC a 30/10 03 UTC para as três estações; os CSVs de setembro têm cobertura zero nessa janela. Reavaliar arquivos de previsão de 28/10 não os torna atuais. Não foram feitas novas consultas de previsão enquanto faltam observações, nem abertos resultados reservados. Os relatórios de previsão mantêm a data original e os bloqueios correspondentes.

## Qualificação e próximos passos

34 testes direcionados aprovados com warnings como erros; Ruff integral de src/tests aprovado; mypy local dos dois módulos alterados aprovado. Regressão integral anterior do merge: 1.099 backend, 56 frontend, mypy 93 módulos, lint/build aprovados. Conferir a regressão remota própria do incremento de preparação; não transferir a aprovação do merge para código posterior.

Para tornar o piloto pronto: obter observações recentes por fonte legítima, verificar qualidade/contratos e cobertura, renovar o preflight pontual, revisar o calendário se seus slots vencerem, repetir a qualificação e registrar a decisão de execução aplicável. Não existe evidência de ganho real da candidate-1. Teste auditivo PT/EN, distribuição/comercial e hospedagem permanecem pendências separadas; horizonte de 14 dias continua somente planejado.
