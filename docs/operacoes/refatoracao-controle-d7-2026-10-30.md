# Refatoração, revisão transversal e infraestrutura D+7 — 30/10/2026

## Resultado e versão

Backend/frontend continuam em **0.1.0**, develop, janela pública **14/7**, reference-v1 padrão. Implementada infraestrutura separada do controle D+7; execução permanece desativada. Revisão estrutural concluída antes de commit/push, conforme solicitado. Não há nova release, fitting, promoção da candidata ou deploy.

## Refatoração aplicada

| Área | Mudança | Efeito |
|---|---|---|
| API | Um handler para as duas classes de erro de validação; leitura da lista de erros uma vez | Remove duplicação mantendo códigos, prioridade e envelope HTTP |
| Cache | Catálogo único de campos numéricos usado para codificar, validar e reconstruir o dia | Evita três listas divergentes; formato e regras preservados |
| Formulário | Validação de envio reutiliza o limite final já calculado para o campo | Remove cálculo paralelo do período máximo |
| Aplicação frontend | `App.vue` usa `toRiskQueryPayload`, antes existente somente nos testes | Uma montagem de consulta para cidade/coordenadas; preserva comportamento da data final |
| D+7 | Execução/calendário, transporte/arquivos e ledger/orçamento em módulos próprios | Responsabilidades explícitas, sem nova abstração no pipeline congelado |

Módulos D+7: `src/climaprev/tools/experimental_d7_control.py`, `experimental_d7_archive.py` e `experimental_d7_ledger.py`. API pública, resposta OpenAPI, TTLs e política meteorológica não foram alterados.

## Controle D+7 implementado

- Calendário completo, prospectivo, versionado e desativado por padrão; exige protocolo próprio, objetivo secundário exploratório, somente D+7 e alvos em desenvolvimento.
- Slots de 18 UTC, prazo de 30 minutos, datas estritamente futuras no planejamento e registro E1 específico antes de executar. E1 do piloto não autoriza este protocolo.
- Ledger próprio, reserva antes de HTTP, limite de 30 requisições diárias incluindo falhas, bloqueio de duplicidade e ausência de retentativa silenciosa.
- Coordenação conservadora: leitura do histórico inteiro do piloto; só admite D+7 quando todos os pares atingirem 14 capturas, sem reservas pendentes e após todas as datas de manifestos fornecidos. Não executa concorrentemente com a coleta ativa. A cauda de observações pode continuar separadamente.
- Workspace D+7 fora da pasta do piloto, impedindo reutilização de seu ledger ou diretórios de arquivos.
- Resposta original preservada como bytes do corpo HTTP descomprimido, sem reserializar JSON; horário, parâmetros efetivos, status, tamanho e hash registrados. Erros HTTP com corpo também ficam rastreáveis; resposta excessiva ou interrompida é falha, sem afirmar corpo integral disponível.
- Uma chamada solicita o dia alvo e o seguinte com timestamps epoch e fuso explícito. Isso inclui o fechamento horário do alvo. Um recorte diário derivado é entregue ao **mesmo adaptador** e à política v1; os parâmetros originais do adaptador e os parâmetros efetivos ficam registrados separadamente.
- O escopo versionado é `adapter_policy_d7_epoch_two_day_transport_v1`: não é repetição byte a byte da requisição pública nem do controle v5. Não representa cache, avisos, geocodificação ou identidade conhecida de rodada. Comparações com o piloto congelado não são retroativas.
- Chuva horária completa e precipitação diária disponível são exigidas para elegibilidade exploratória. Valores diário e horário são preservados separadamente; não se assume identidade entre suas agregações. Grade retornada e ponto solicitado também são separados, sem certificar representatividade.
- Arquivos de captura verificáveis por hash; corrupção do JSON ou do corpo original é detectada. Hash é integridade local, não autenticação independente da origem.

## Segunda e terceira revisões do projeto

Inventário transversal de **618 entradas** versionadas/de implementação, leitura dirigida de backend, frontend, ferramentas, testes, configuração/CI e documentação; busca AST por funções grandes e corpos duplicados. O inventário não equivale a revisão humana de cada linha nem prova ausência de defeitos.

A segunda passagem encontrou e corrigiu a montagem duplicada da consulta no App. O único corpo Python idêntico de tamanho relevante restante nessa busca corresponde a declarações de métodos em Protocol, não implementação descartável. Catálogos de tradução, regras de segurança, scripts de reprodução e validação runtime são conteúdo necessário.

Funções extensas em `historical_experiment`, `experimental_comparison`, `experimental_evaluation`, `experimental_coverage` e demais módulos científicos são oportunidades de manutenção futura. Vários pertencem ao fingerprint congelado do piloto. Não há falha demonstrada que justifique trocar suas versões durante a coleta: qualquer reorganização deve ser deliberada e preservar evidências. Isso não significa declarar o projeto livre de futuras refatorações.

## Linhas e limites da medição

Escopo: `src/**/*.py` e `frontend/src/**/*.{ts,vue,css}`, excluindo `.test.ts`. Base `355a158`: **13.400 linhas físicas**. Arquivos existentes após limpeza: **13.358**, redução de **42**. Infraestrutura D+7 nova: **463 linhas** em três módulos. Total no escopo: **13.821**, crescimento líquido de **421** por funcionalidade nova. Testes/documentação ficam fora dessa métrica. Não apresentar redução local como redução global.

## Qualificação

- Linux/Redis isolado: **1.207 testes backend aprovados**, warnings como erros, Ruff integral e mypy em **102 módulos**.
- Node.js **22.23.2**: **61 testes frontend**, ESLint, tipagem e build aprovados.
- D+7: **37 testes** de janela, UTC/fusos/virada do ano/DST, autorização, quota do piloto, isolamento, orçamento, falhas, resposta bruta, hora final, duplicidade e corrupção.
- Comparação diferencial do cache contra `355a158`: codificação idêntica e sete casos de decodificação equivalentes.
- OpenAPI canônico preservado: `474199bf4155eec9bde52b4343e0aaed12888bee7315f9e87460b48efaac62fe`.
- Calendário ativo v5 validado com o código atual; nenhum módulo do pipeline congelado foi alterado. Nenhuma previsão real nova foi solicitada nesta implementação.

[Evidência estruturada](evidence/refatoracao-controle-d7-2026-10-30.json). Os checks remotos devem ser conferidos no SHA desta publicação; os de `355a158` já foram aprovados e permanecem histórico.

A terceira revisão acrescentou bloqueios para slots equivalentes em UTC e semente sem todos os pares estação/modelo, além de testes reais do caminho de captura em dias civis de 23/25 horas e concorrência do orçamento. Regressão posterior: 1.207 testes backend aprovados.

## Operação e pendências

Ler o [manual D+7](controle-d7-operacao-2026-10-30.md). A infraestrutura está implementada/testada, mas não há campanha D+7 real ativada. Faltam calendário e partições prospectivos próprios, registro de execução e verificação de disponibilidade sob esse desenho antes da coleta. Não reaproveitar reservas/arquivos do piloto.

A revisão de [metadados instrumentais](../planejamento/reference-candidate-1/metadados-instrumentais-2026-10-30.md) continua com lacunas: nova busca oficial não encontrou fichas individuais de altura/calibração para A201/A001/A801. Não houve contato externo. Teste auditivo PT/EN, licenciamento/atribuições e confirmação científica continuam independentes. [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).

[Terceira revisão concluída, achados e verificações](terceira-revisao-refatoracao-2026-10-30.md).
