# Piloto técnico — observações restauradas e reposição por cota

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Resultado e autorização

Em 30/10/2026, a consulta normal do sistema TEMPO carregou observações e permitiu baixar CSVs de A201, A001 e A801, de 23 a 30/10. A API direta foi repetida e continua retornando 204 nas três. O problema não é ausência demonstrada das medições: o acesso pela interface oficial funcionou nesta sessão. O aviso de cota do reCAPTCHA permaneceu na página, mas não impediu a consulta. Não foram gerados/reutilizados tokens, resolvidos desafios ou contornados controles.

O usuário autorizou explicitamente o agendamento diário, ciente de que o notebook pode desligar, descarregar ou ficar sem Codex. Depois determinou a reposição em dias seguintes até a cota. A regra vigente é **14 capturas elegíveis de previsão D+1 por estação/modelo**, totalizando 210, com datas futuras próprias. Falhas, horários perdidos e reservas incompletas permanecem no histórico e na cobertura; não são previsões retroativas.

A automação `piloto-t-cnico-climaprev` é diária, às 15h de Brasília, nesta conversa. A primeira data de coleta é 31/10, na janela 18:00–18:30 UTC. As 14 datas de 31/10 a 13/11 são a programação inicial, não um encerramento obrigatório após perdas. Não há garantia de execução com computador ou Codex indisponíveis. Não foi instalado serviço de energia, inicialização ou despertar do notebook.

## Dados e qualidade

Os três CSVs originais têm 192 linhas horárias por estação. Na conversão realizada, 184 endpoints já decorridos foram preservados e oito linhas futuras inteiramente vazias foram omitidas, com contagem explícita. Linhas futuras com qualquer valor seriam rejeitadas. Na janela concluída de 23/10 03 UTC a 30/10 03 UTC, chuva e rajadas têm 168/168 horas válidas nas três estações. Isso comprova cobertura dessa janela; não certifica calibração, altura ou representatividade.

O exportado pelo TEMPO não contém identidade da estação no próprio CSV. `inmet_tempo_csv.convert_tempo_csv` exige vínculo explícito com URL, estação exibida e catálogo. Preserva hashes dos bytes originais e normalizados, mapeamento de colunas e metadados. Esse vínculo é rastreabilidade declarada da obtenção, não autenticação criptográfica do provedor. O importador anual histórico permanece inalterado. A temperatura rotulada `Inst.` na interface não foi transformada em observação instantânea nem média anual compatível; seu uso permanece bloqueado. Umidade mantém a semântica não resolvida. Ausência de valor não vira zero.

Preflight novo: 15/15 jobs concluídos, com arquivos imutáveis e ledger diagnóstico próprio. Os cinco braços cobrem chuva D+1 nas três estações. D+3 de MET e D+7 de MET/ICON seguem sem soma diária elegível; baseline pública não cobre D+7. Prontidão técnica de chuva passou. Não houve ajuste da candidata, uso de novos resultados reservados, confirmação ou promoção. Reference-v1 permanece padrão.

## Arquivos operacionais

Diretório local: `.report-work/inmet-browser-2026-10-30/`.

- `A201-original.csv`, `A001-original.csv`, `A801-original.csv`: downloads originais preservados.
- `*-normalized.csv`, `*-provenance.json`, `*-quality.json`: conversões e qualidade.
- `forecast-archives/`, `diagnostic-preflight.*`, `readiness-v4.json`: diagnóstico de 30/10, **não contam na cota do piloto**.
- `protocol-v5-adaptive.json`, `approval-E1-v5.json`, `calendar-v5-seed.enabled.json`: protocolo adaptativo, autorização técnica e programação inicial.
- `pilot-ledger.sqlite`: ledger único do piloto, criado vazio na preparação; nunca substituir por outro para repetir chamadas.
- `pilot-archives/`: arquivos futuros do piloto; `extension-manifests/`: cada manifesto adicional prospectivo; `slot-results/`: resultado de cada execução, inclusive ausência/falha.

O calendário fixo v4 foi desativado e superado; não executá-lo. O protocolo adaptativo versionado está em `docs/planejamento/reference-candidate-1/protocolo-piloto-adaptativo-2026-10-30.json`. O E1 registra autorização de coleta técnica; E2/E3 não foram concedidos. O hash inclui o novo importador e o planejador de cota. Se código/versões não coincidirem, interromper e relatar; não reescrever hashes para fazer passar.

## Rotina diária

1. Conferir relógio UTC, integridade, E1 e versões. Fora de 18:00–18:30 UTC não capturar previsões atrasadas sob o slot antigo. Auditar slots vencidos e registrar ausências ao retomar.
2. Nas datas iniciais de 31/10 a 13/11, executar o calendário semente com o mesmo ledger. As chamadas são deduplicadas por job; reservas falhadas/interrompidas não são repetidas no mesmo slot.

```powershell
$env:PYTHONPATH = 'src'
.venv/Scripts/python.exe -m climaprev.tools.experimental_campaign --calendar .report-work/inmet-browser-2026-10-30/calendar-v5-seed.enabled.json --ledger .report-work/inmet-browser-2026-10-30/pilot-ledger.sqlite --output .report-work/inmet-browser-2026-10-30/pilot-archives
```

3. Preservar o resultado de cada execução em arquivo novo. A lista histórica inclui todos os manifestos da semente, mesmo ausentes, e todos os manifestos de extensão já planejados. Não contar somente os dias bem-sucedidos na cobertura.
4. Usar `audit_quota_progress` em `climaprev.tools.experimental_pilot_quota` com protocolo v5, histórico completo de manifestos, ledger e relógio atual. Só contam capturas arquivadas, com hash/modelo/ponto/horário conferidos e chuva D+1 completa. Arquivos ausentes/corrompidos ou D+1 incompleto não satisfazem a cota; a falha permanece registrada. `completed_dates` desse resultado é a entrada de planejamento, não um contador inventado.
5. Após o período semente, usar `plan_quota_slot` com esse progresso e o próximo slot diário novo. O planejador recusa datas vencidas, duplicadas/futuras nas declarações de conclusão e cotas acima de 14; não inclui pares já completos nem uma segunda captura do mesmo par no mesmo dia. Habilitar o plano somente com E1 v5. Salvar os novos manifestos de maneira exclusiva em `extension-manifests/` **antes** de executar. Usar `run_manifest` com os mesmos ledger, diretório de arquivos e cliente HTTP limitado da campanha. Não editar o calendário semente para fingir que já previa essas datas.
6. Quando a cota de um par chegar a 14, parar suas chamadas. Quando todos os 15 pares chegarem a 14, parar todas as previsões. Acompanhamento observacional segue até o fim do último alvo D+7 real: última data de captura aceita + sete dias, mais o endpoint final no dia seguinte. Essa cauda também se desloca se houver reposições.
7. Depois das previsões, obter observações pelo fluxo normal das três tabelas TEMPO, preservando originais e catálogo em pasta datada nova. Converter com o adaptador explícito; manter data real de obtenção e lacunas. Recuperar observações publicadas de datas passadas é permitido com proveniência; isso não autoriza reconstruir uma previsão perdida.
8. Relatar bloqueios, perdas de cobertura relevantes e conclusão; ficar em silêncio sem mudança relevante. Não fazer fitting, confirmação, E2/E3, promoção, main, deploy ou push automático. Ao completar a cota e a cauda observacional disponível, entregar relatório de cobertura/limitações e pausar a automação `piloto-t-cnico-climaprev` sem arquivar a conversa.

O relógio de uma tentativa nova pertence a ela. Falha na terça e captura na quarta contam como uma ausência na terça e uma captura na quarta. Não contar a quarta duas vezes. A cota controla capturas por par; datas distintas entre modelos podem reduzir a interseção comparável e não garantem 14 dias comuns completos ou suporte para extremos.

## Calendário científico

### Relatório automático de acompanhamento e encerramento

O módulo de análise `experimental_pilot_report` pode ser usado pela rotina diária e no fechamento, sem modificar o pipeline de coleta. Exemplo, definindo `PYTHONPATH=src` e usando um nome novo para cada saída:

```powershell
.venv/Scripts/python.exe -m climaprev.tools.experimental_pilot_report --protocol .report-work/inmet-browser-2026-10-30/protocol-v5-adaptive.json --calendar .report-work/inmet-browser-2026-10-30/calendar-v5-seed.enabled.json --ledger .report-work/inmet-browser-2026-10-30/pilot-ledger.sqlite --observations A201=CAMINHO_CSV_A201 --observations A001=CAMINHO_CSV_A001 --observations A801=CAMINHO_CSV_A801 --output CAMINHO_NOVO_RELATORIO.json
```

Acrescentar `--manifest CAMINHO_MANIFESTO_EXTENSAO.json` para **cada** manifesto adicional já planejado, inclusive falhas. O relatório não descobre extensões omitidas sem registro no ledger. `technical_pilot_complete` só fica verdadeiro após a cota e a observação dos alvos reais completos; não significa aprovação científica. A automação pode usar esse resultado para compor o relatório final e verificar sua condição de pausa.

As reposições são motivadas exclusivamente por disponibilidade, nunca por chuva observada ou desempenho. Cada extensão declara novos alvos antes de coletar. `requires_partition_replan` sinaliza quando D+7 ultrapassa o fim condicional de desenvolvimento. Nesse caso o calendário científico de seleção/confirmação antigo deve ser considerado indisponível para uso: revisar e registrar novos embargos/congelamentos antes de qualquer pesquisa confirmatória. Não mover dados reservados nem alterar protocolos históricos. A reposição técnica autorizada não é uma ampliação oportunista da confirmação científica.

## Qualificação

Adaptador TEMPO: oito testes de valores/unidades, ausência, dados futuros, identidade, duplicação e limites. Planejador/auditor de cota: dez testes de nova identidade temporal, parada por par, duplicação, E1, relógio vencido, histórico perdido e integridade de arquivo. Ruff e mypy dos módulos novos aprovados. Regressão remota integral do novo incremento deve ser conferida no próprio SHA; a aprovação anterior de 1.104 testes é do commit 0471a98.

A primeira tentativa de automação foi rejeitada pela revisão automática por falta de autorização explícita para recorrência. Após a resposta humana autorizando o agendamento, a automação foi criada. A política de reposição passou a integrar esse acompanhamento por determinação posterior do usuário. Até a primeira janela futura, nenhum slot de piloto foi executado.

Atualização de autorização: a retirada do limite de 21/11 foi inicialmente rejeitada pela revisão automática por criar recorrência potencialmente indefinida. O usuário respondeu explicitamente “Autorizar até completar, sem data-limite”; a atualização foi então aceita. A rotina não tem término fixo no scheduler e deve ser pausada ao concluir cota e cauda observacional.
