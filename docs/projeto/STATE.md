# STATE — estado atual do ClimaPrev

## Integração estável preparada — 31/10/2026

Backend privado ClimaPrev-API qualificado em `225541e` por CI/Security próprios. Main do projeto geral recebe a develop via promoção revisada, com código funcional preservado e conflitos documentais resolvidos; [proveniência e critérios](../operacoes/promocao-develop-main-2026-10-31.md). O histórico Git/PR registra o SHA efetivamente integrado. Sem promoção científica ou deploy.

Atualização: 30/10/2026. [Índice contextual](../contexto/README.md) · [Estado](STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md)

## Backend independente entregue — 31/10/2026
+
+ClimaPrev-API recebeu somente o backend funcional do snapshot `90c61b5`, com política reference-v1 e janela 14/7. Importação inicial privada `630beba`, 550 testes operacionais, Ruff/mypy em 51 módulos, builds autônomos, HTTP/HTTPS/CORS e segurança locais aprovados. Pesquisa/candidate-1 e piloto permanecem no monorepo. [Entrega, diferenças e checks próprios](../operacoes/extracao-api-backend-2026-10-31.md). Isso conclui a extração operacional inicial; produção, licença e recursos comerciais continuam escopos próprios.
+
+## Publicação conferida — 31/10/2026
+
+Implementação D+7 e refatoração publicadas em `b2894b3`. [CI aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41154650970) e [Security aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41154650954) nesse SHA. Complemento posterior inclui os READMEs do frontend/gate e limpa formatação do callback D+7; AST Python idêntica, sem alteração funcional. Métrica ajustada: 461 linhas novas D+7 e redução de 42 nos arquivos existentes. Checks do complemento devem ser conferidos no próprio SHA. Piloto preservado e D+7 desativado.
+
+## Refatoração revisada e infraestrutura D+7 — 30/10/2026

Limpeza de duplicações de handlers, campos do cache, limite de datas e montagem de consultas concluída. Segunda revisão transversal corrigiu a consulta duplicada no App; terceira revisão endureceu unicidade dos slots UTC e completude dos pares da semente, com 37 testes D+7 aprovados. D+7 agora tem três módulos separados: execução/calendário, transporte/arquivo bruto e ledger/orçamento. Implementação desativada, sem alterar o piloto, a API 14/7 ou a reference-v1. Execução D+7 aguarda protocolo/calendário/E1 próprios e conclusão da quota de previsões do piloto; não roda concorrentemente com ele.

Regressão local Linux: **1.207 testes backend**, Ruff e mypy em **102 módulos**; frontend Node.js 22: **61 testes**, lint/tipagem/build. OpenAPI preservado e cache equivalente à base. Redução de **42 linhas nos arquivos de runtime existentes**, com **461 linhas novas de D+7**; total no escopo medido cresce 419, sem alegação de redução global. Metadados instrumentais individuais ainda não comprovados, candidata sem superioridade demonstrada. [Entrega, revisão e limites](../operacoes/refatoracao-controle-d7-2026-10-30.md).

## Estado consolidado

Backend e frontend **0.1.0**, branch **develop**, monorepo com builds e execução separados. Base funcional publicada: `ffa50f11cf0a4b0e68acdd249f80d0c8f8abca15` (`ffa50f1`); esta revisão documental é posterior a essa base, sem nova release.

Janela pública **14/7** concluída: consultas de um a sete dias consecutivos entre hoje UTC e +13, inclusive. O calendário da interface e a API GET/POST aplicam os mesmos limites. A agregação meteorológica mantém o fuso da localidade. Disponibilidade pontual na segunda semana verificada; isso não comprova precisão.

Qualificação da base: **1.170 testes backend**, mypy em **99 módulos**, **60 testes frontend**, Ruff, tipagem, lint e build aprovados. [CI aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906751) e [Security gates aprovado](https://github.com/0SunnyBoy/climaprev/actions/runs/41150906743) no SHA `ffa50f1`. A revisão documental publicada em `355a158` também passou [CI](https://github.com/0SunnyBoy/climaprev/actions/runs/41152086801) e [Security](https://github.com/0SunnyBoy/climaprev/actions/runs/41152086839). Esses resultados não qualificam automaticamente alterações posteriores.

**Reference-v1 permanece padrão.** A infraestrutura das duas frentes da candidate-1 está integrada: fontes/coleta/arquivos, normalização, pareamento, cobertura, comparação, incerteza, revisão instrumental, variantes fixas e relatório técnico do piloto. Não há superioridade real demonstrada, fitting concluído, seleção confirmada ou promoção.

Observações recentes das estações A201, A001 e A801 foram obtidas pela interface oficial TEMPO, com originais e proveniência preservados; a API direta retornou 204 na última verificação. Preflight diagnóstico de 30/10: 15/15 braços/pontos disponíveis para D+1, sem contar para a cota. Não generalizar esse resultado para todos os horizontes ou variáveis.

Piloto adaptativo v5 autorizado e agendado diariamente às **15h de Brasília**, janela 18:00–18:30 UTC, a partir de 31/10. Meta: **14 capturas elegíveis por estação/modelo, 210 ao todo**, sem data-limite fixa. Perdas são preservadas e repostas em novas datas futuras; sem backfill. Encerrar previsões por par ao atingir a cota e acompanhar a cauda observacional até o último D+7 real. Notebook/Codex indisponíveis podem perder slots. Estado da preparação: zero capturas do piloto; progresso posterior exige auditoria do ledger, não inferência a partir do agendamento.

O protocolo e os hashes congelados do piloto foram preservados. A ampliação pública 14/7 não acrescenta D+7 retroativamente ao controle experimental de sete datas. Novo controle ou alteração de partições requer versão metodológica explícita; reposições que invadam partições condicionais exigem replanejamento antes da análise. Sem abertura indevida de reservas, E2/E3, promoção, merge na main ou deploy.

## Pendências e sequência

1. Executar e acompanhar o piloto autorizado; auditar capturas, perdas, reposições, CSVs, pareamento, cobertura e cauda observacional.
2. Obter as fichas oficiais ainda ausentes e fechar equivalência instrumental com metadados reais (revisão documental e inventário já concluídos): temperatura, umidade e vento/rajada respeitam janelas, agregações, alturas e representatividade. Diagnóstico automatizado não certifica equivalência.
3. Consolidar suporte por estação/variável/antecedência, critérios de extremos, tamanho de bloco e validade dos intervalos/multiplicidade com os dados elegíveis. Critérios condicionais não viram critérios confirmatórios por existência de código.
4. Preparar protocolo/calendário/E1 próprios e verificar disponibilidade para executar a infraestrutura D+7 já implementada, somente após a quota de previsões do piloto; replanejar partições se necessário, preservando o protocolo congelado e sem usar resultados reservados para escolher ajustes.
5. Refinar e comparar variantes apenas nas partições permitidas; congelar candidata, confirmar fora da amostra e obter aceite final antes de integrar/promover. Melhoria de precisão ainda não demonstrada.
6. Concluir teste auditivo real com leitor de tela em português e inglês; automação não substitui esse ensaio.
7. Definir licença, atribuições e condições de distribuição/uso comercial das fontes antes da oferta de serviços. Infraestrutura de hospedagem e monitoramento definitivo permanece adiada pelo usuário.

16/8 e previsão sazonal continuam fora do escopo. A extração operacional inicial do backend foi entregue no ClimaPrev-API, com proveniência e validação próprias. Documentos acadêmicos ficam fora da manutenção do projeto.

## Evidências e histórico

[Entrega e qualificação 14/7](../operacoes/horizonte-14-consulta-7-2026-10-30.md) · [Ferramentas analíticas](../operacoes/frente-2-prioridades-4-1-2-3-2026-10-30.md) · [Checkpoints anteriores](STATE-REGISTROS-ATE-2026-10-30.md)
