# Consolidação da develop — 27/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Entrega

Consolidação dos incrementos locais desde a base 5a6fc9c: arquivo imutável, coletores GFS/IFS/ICON/MET, normalização, baseline operacional, manifesto e ledger local, pareamento observacional e comparador exploratório de chuva. Inclui testes de entrega dos avisos de chuva/vento/calor/frio, unidades °C/°F e mensagem acessível estável para HTTP 429.

Auditoria identificou dois achados moderados no Vitest 5.0.2. Lockfile atualizado dentro das versões compatíveis, incluindo Vitest 5.0.5. Instalação reproduzível e auditoria repetidas sem vulnerabilidades.

## Verificação local

- 748 testes backend aprovados em 66,17 s, com warnings como erros, em Docker/Redis isolado na base 15.
- Mypy: 82 módulos aprovados; Ruff src/tests aprovado.
- Frontend: 48 testes, ESLint, vue-tsc e build aprovados após correção do lockfile.
- npm audit: zero vulnerabilidades após correção.
- Hardening local e git diff --check aprovados.

## Limites e sequência

Publicação e resultado de CI/Security devem ser conferidos para o SHA consolidado; execução local não certifica os checks remotos. Sem merge em main ou implantação. Reference-v1 permanece ativa, sem promoção ou ganho científico comprovado da candidate-1.

Próximos: teste auditivo real PT/EN; fechar parâmetros/calendário e controle D+7; equivalência e pareamento das demais variáveis; cobertura contra calendário e incerteza; coleta recorrente somente após aceite; avaliação independente, refinamento e integração condicionada. A aprovação da direção não aprova automaticamente parâmetros quantitativos propostos.

## Complemento operacional

Implementado `audit_calendar` em `tools/experimental_coverage.py`: lê ledger SQLite em modo somente leitura e confronta todos os jobs dos manifestos fornecidos. Distingue futuro, aberto, perdido, concluído, falho e reserva vencida; planos inativos ficam fora do denominador devido. Rejeita duplicatas, adulteração do manifesto e intervalos inválidos. Detecta jobs de outras campanhas sem adicioná-los ao denominador.

43 testes direcionados (calendário, campanha e comparador), mypy do novo módulo e Ruff aprovados. O calendário fornecido precisa ser completo: manifestos omitidos não podem ser detectados. Job concluído não comprova integridade do arquivo, pontualidade da entrega ou dia meteorológico elegível. A cobertura por alvo/variável e sua ligação aos pares científicos continuam pendentes. Não foi criada rotina recorrente.

Usuário solicitou revisão dos parâmetros antes do aceite; resumo em `docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md`. Campanha não iniciada.

## Qualificação integral do complemento

757 testes backend aprovados em 58,27 s; mypy em 83 módulos e Ruff aprovados. Os 48 testes frontend/build/lint/auditoria são da mesma versão de frontend, sem alterações posteriores. Nove novos testes de calendário cobrem slots ausentes, estado inativo, denominadores, reservas, duplicação e integridade; nenhum dado meteorológico real novo foi avaliado.

Security do primeiro commit 4525202 aprovado: https://github.com/0SunnyBoy/climaprev/actions/runs/40541368589. CI desse commit ainda aguardava a etapa de navegador na última consulta; o complemento requer seus próprios checks remotos. Não inferir aprovação do SHA seguinte a partir do anterior.
