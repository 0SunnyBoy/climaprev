# Datas e fusos — correção da janela pública em 20/10/2026

Atualização em 30/10/2026: janela pública ampliada para hoje UTC até +13, com até sete dias por consulta. [Contrato vigente e verificações](../operacoes/horizonte-14-consulta-7-2026-10-30.md). O conteúdo abaixo registra o checkpoint histórico de 20/10.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../../RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Comportamento implementado

Mantida a janela de **sete datas**: hoje UTC até hoje UTC + 6, inclusive, com até sete dias consecutivos por consulta. Data final omitida equivale à inicial. Não foi ativado o horizonte de 14 dias; ele está somente planejado no RDP por orientação do usuário.

GET e POST `/api/v1/risk` verificam a janela antes de chamar o serviço de previsão, incluindo resolução da localização, cache e provedores. Datas passadas ou posteriores ao limite retornam `422 INVALID_PERIOD` no envelope de erro existente. A validação estrutural de datas e de período invertido continua no schema. A validação temporal não foi aplicada às ferramentas offline de pesquisa histórica.

O corte UTC determina elegibilidade de solicitações; não converte os dias meteorológicos em dias UTC. Dados e agregações da previsão continuam usando o fuso efetivo do local retornado pelo provedor. O fuso do navegador ou do servidor não muda os limites. É uma janela pública conservadora do produto, não uma afirmação de que todos os modelos têm somente sete dias de alcance.

## Interface

Os campos de data recebem limites mínimo/máximo e explicação em PT/EN com o corte UTC. O fim não pode preceder o início. A janela é atualizada a cada 30 segundos, ao retornar foco/visibilidade e antes de enviar, preservando o valor digitado para que uma data expirada seja corrigida pelo usuário. Timers e listeners são removidos ao desmontar o componente.

O relógio do navegador fornece orientação de calendário; a API continua sendo a autoridade. Relógio local incorreto pode levar a rejeição 422 e deve ser corrigido. Não foi criado endpoint de sincronização de relógio. A validade temporal é verificada no início da execução da consulta, não reinterpretada no meio de uma resposta em andamento.

## Testes e reprodução

- Testes de UTC com offsets -12, -3, 0 e +14, virada de ano e relógio sem timezone.
- Limites inclusivos de hoje/último dia e rejeição de ontem/dia posterior ao limite; GET e POST verificam ausência de chamadas ao serviço quando inválidos.
- Teste de formulário aberto na virada de meia-noite UTC: limites mudam e data expirada não é enviada.
- Fixtures de integração usam relógio público fixo em 28/08/2026 para manter os dados sintéticos determinísticos; isso não desativa a validação. Os testes de limites exercitam aceites e rejeições desse mesmo relógio.
- Gate HTTPS do desacoplamento ampliado para verificar limites do calendário e respostas 422 reais. A bancada monta o código fonte da API somente para teste.

Validações: `pytest tests/unit/api/test_forecast_window.py tests/unit/api/test_risk_schema.py`, testes de integração da API e suíte completa; frontend `npm test`, `npm run lint` e `npm run build`; gate documentado em `tests/docker/decoupling/README.md`. Os resultados efetivamente executados são registrados no RDP.

Resultado final: 618 testes backend aprovados em 39,65 s, sem exclusões, e 20 frontend aprovados. Build/typecheck/ESLint/Ruff/mypy, gate HTTPS com datas e smoke integrado HTTP aprovados. A regressão inicial expôs herança indevida de hosts de implantação nos testes ASGI; a fixture agora isola essa variável e cada teste continua podendo definir sua allowlist. Casos de horário de verão usam relógio correspondente ao próprio dia sintético. O teste completo final usou a imagem construída com os arquivos de fixtures/schema corrigidos montados individualmente. Nenhuma proteção de produção foi removida.

## Pendências separadas

Horizonte de 14 dias não implementado. Sua retomada requer ampliar de forma consistente limites, orientação da segunda semana, cobertura de variáveis e testes, preservando sete dias por consulta. Não há validação científica em D+14, alteração de reference-v1 ou ajuste/calibração neste incremento.
