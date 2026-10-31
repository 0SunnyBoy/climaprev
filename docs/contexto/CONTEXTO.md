# Contexto de retomada — ClimaPrev

Atualização: 30/10/2026. [Índice contextual](README.md) · [Estado](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md)

## Estado consolidado

Backend e frontend **0.1.0**, branch **develop**, monorepo com builds e execução separados. Base funcional publicada: `ffa50f11cf0a4b0e68acdd249f80d0c8f8abca15` (`ffa50f1`); esta revisão documental é posterior a essa base, sem nova release.

Janela pública **14/7** concluída: consultas de um a sete dias consecutivos entre hoje UTC e +13, inclusive. O calendário da interface e a API GET/POST aplicam os mesmos limites. A agregação meteorológica mantém o fuso da localidade. Disponibilidade pontual na segunda semana verificada; isso não comprova precisão.

Qualificação da base: **1.170 testes backend**, mypy em **99 módulos**, **60 testes frontend**, Ruff, tipagem, lint e build aprovados. [CI aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906751) e [Security gates aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906743) no SHA `ffa50f1`. Esses resultados não qualificam automaticamente commits posteriores.

**Reference-v1 permanece padrão.** A infraestrutura das duas frentes da candidate-1 está integrada: fontes/coleta/arquivos, normalização, pareamento, cobertura, comparação, incerteza, revisão instrumental, variantes fixas e relatório técnico do piloto. Não há superioridade real demonstrada, fitting concluído, seleção confirmada ou promoção.

Observações recentes das estações A201, A001 e A801 foram obtidas pela interface oficial TEMPO, com originais e proveniência preservados; a API direta retornou 204 na última verificação. Preflight diagnóstico de 30/10: 15/15 braços/pontos disponíveis para D+1, sem contar para a cota. Não generalizar esse resultado para todos os horizontes ou variáveis.

Piloto adaptativo v5 autorizado e agendado diariamente às **15h de Brasília**, janela 18:00–18:30 UTC, a partir de 31/10. Meta: **14 capturas elegíveis por estação/modelo, 210 ao todo**, sem data-limite fixa. Perdas são preservadas e repostas em novas datas futuras; sem backfill. Encerrar previsões por par ao atingir a cota e acompanhar a cauda observacional até o último D+7 real. Notebook/Codex indisponíveis podem perder slots. Estado da preparação: zero capturas do piloto; progresso posterior exige auditoria do ledger, não inferência a partir do agendamento.

O protocolo e os hashes congelados do piloto foram preservados. A ampliação pública 14/7 não acrescenta D+7 retroativamente ao controle experimental de sete datas. Novo controle ou alteração de partições requer versão metodológica explícita; reposições que invadam partições condicionais exigem replanejamento antes da análise. Sem abertura indevida de reservas, E2/E3, promoção, merge na main ou deploy.

## Pendências e sequência

1. Executar e acompanhar o piloto autorizado; auditar capturas, perdas, reposições, CSVs, pareamento, cobertura e cauda observacional.
2. Fechar equivalência instrumental com metadados reais: temperatura, umidade e vento/rajada respeitam janelas, agregações, alturas e representatividade. Diagnóstico automatizado não certifica equivalência.
3. Consolidar suporte por estação/variável/antecedência, critérios de extremos, tamanho de bloco e validade dos intervalos/multiplicidade com os dados elegíveis. Critérios condicionais não viram critérios confirmatórios por existência de código.
4. Versionar o controle científico de D+7 e replanejar partições se necessário, preservando o protocolo congelado e sem usar resultados reservados para escolher ajustes.
5. Refinar e comparar variantes apenas nas partições permitidas; congelar candidata, confirmar fora da amostra e obter aceite final antes de integrar/promover. Melhoria de precisão ainda não demonstrada.
6. Concluir teste auditivo real com leitor de tela em português e inglês; automação não substitui esse ensaio.
7. Definir licença, atribuições e condições de distribuição/uso comercial das fontes antes da oferta de serviços. Infraestrutura de hospedagem e monitoramento definitivo permanece adiada pelo usuário.

16/8, previsão sazonal e extração de repositório não foram implementados nesta entrega. O plano de extração é uma proposta separada. Documentos acadêmicos ficam fora da manutenção do projeto.

## Retomada segura

Ler [manual do piloto](../operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md) antes de operar a coleta. Usar protocolo-v5, E1 v5, calendário semente, extensões, `pilot-ledger.sqlite` e `pilot-archives/` da pasta `.report-work/inmet-browser-2026-10-30/`. Auditar com `audit_quota_progress`; extensões devem ser futuras, salvas antes da execução, e apenas para pares abaixo da cota. Não contar preflight nem reabrir reservas falhadas. Preservar alterações de outras tarefas e originais observacionais.

## Evidências e histórico

[Entrega e qualificação 14/7](../operacoes/horizonte-14-consulta-7-2026-10-30.md) · [Ferramentas analíticas](../operacoes/frente-2-prioridades-4-1-2-3-2026-10-30.md) · [Checkpoints anteriores](CONTEXTO-REGISTROS-ATE-2026-10-30.md)
