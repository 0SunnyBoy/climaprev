# Refatoração transversal e limpeza — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Revisão posterior das linhas e abstrações

A medição foi separada entre implementação e testes. Nova simplificação removeu mapeamento repetitivo, encaminhamento intermediário do cache, wrappers triviais e tipo duplicado. **109 linhas físicas retiradas nesta revisão: 18.408 → 18.299**. Contra o commit original 18.104, o saldo ainda é +195: +168 testes/gates e +27 código executável. Não se usa a redução de um módulo como prova de redução global.

Validação mais recente: **659 testes backend em 55,18 s**, 32 frontend, lint/tipagem/build e 24 comparações JSON anterior/novo aprovados; OpenAPI preservado. [Contagem, atribuição e avaliação das abstrações](reducao-linhas-2026-10-20.md). As verificações abaixo registram a execução anterior quando houver diferença de contagem.

## Escopo e resultado

Executada a revisão transversal solicitada: backend, frontend, testes, scripts/gates, configurações de execução e documentação corrente. O inventário cobre os arquivos versionáveis do repositório, incluindo scripts científicos de reprodução; não inclui diretórios privados/ignorados. Inventário/referências e leitura dirigida não equivalem a prova de ausência de todo defeito. [Inventário](evidence/refatoracao-inventario-2026-10-20.json).

Não se reescreveu cada arquivo por obrigação: domínio científico, CSS e modos de execução com uso confirmado foram mantidos. Não houve nova funcionalidade de previsão, promoção da candidata, mudança de horizonte, separação de repositórios ou implantação externa.

## Backend

- `ForecastQueryService` tornou-se orquestrador: local, previsão, avaliação e avisos. Serviços `CachedLocationResolver`, `CachedForecastProvider` e `CachedOfficialAlerts` possuem responsabilidades próprias.
- Recuperação de previsão mantém fresh/stale, backoff, posse do lock, heartbeat, cancelamento, limpeza e expiração. Alertas mantêm tratamento conservador e revalidação na entrega. Serialização/validação do cache ficam em `application/cache_codec.py`.
- DTOs, conversões e prioridade do resultado ficam em `application/query_result.py`. Schemas/mapper HTTP ficam em `api/schemas/risk_response.py`.
- `main.py` concentra composição e recursos; tratamento HTTP de erros e rotas de saúde ficam em módulos da API.
- Exceções são importadas da aplicação. Removidos o módulo redundante `infrastructure/errors.py`, reexports desnecessários em adaptadores e alias `Any` de RiskPolicy. ForecastQueryPort fica junto das portas.

| Arquivo | Linhas no HEAD anterior | Linhas após refatoração |
|---|---:|---:|
| `application/services/forecast_query.py` | 914 | 102 |
| `api/routes/risk.py` | 265 | 64 |
| `main.py` | 288 | 151 |

Responsabilidades úteis foram realocadas; isso não significa redução equivalente no total do projeto nem ganho de velocidade por si só. A construção de ForecastQueryService continua aceitando as mesmas dependências; caminhos internos de DTOs/exceções foram atualizados nos consumidores do repositório, sem shims.

## Frontend e testes

- Prazo/aborto/encerramento da espera centralizados em `utils/requestDeadline.ts`. Debounce, sequência e estados específicos permanecem nos composables, preservando timeout de busca 5 s e consulta 10 s.
- `services/responseValidation.ts` separa validação JSON em execução do transporte HTTP. Guard público existente preservado; tipos de compilação não substituem validação de dados.
- Regras ESLint TS/Vue consolidadas; interface ErrorEnvelope sem referências removida. Compilador passa a rejeitar variáveis e parâmetros sem uso.
- Seletores CSS estáticos e classes de risco dinâmicas têm uso confirmado; não foram apagados por heurística textual.
- Doubles/builders compartilhados movidos para `tests/support/forecast.py`; testes de prazo/alertas/identidade/expiração/lock não importam mais helpers de um módulo de testes de integração. Monkeypatches acompanham o módulo proprietário do algoritmo, sem enfraquecer asserções.

## Configuração e automação

O verificador de hardening estava obsoleto: procurava Nginx no Compose e assumia quantidades antigas de serviços. Agora lê a configuração efetiva, verifica cada serviço, imagens fixadas, privilégios/capabilities, filesystem/tmpfs e rede privada. A configuração expandida permanece em memória, sem imprimir ambiente/segredos. Gate conectado aos dois workflows; oito regressões cobrem aumento de serviços e falta das proteções exigidas.

Composes integrado, API, frontend independente e overlay de desenvolvimento validados. Nenhum desses modos foi removido como supérfluo. Dependências/locks utilizados por execução, build, teste e carga preservados; sem bibliotecas adicionadas ou atualização incidental de versões.

## Documentação e conteúdo preservado

README, frontend README, CONTEXTO, visão geral, PROJECT, STATE, ROADMAP, handoff e catálogo técnico consolidados. Retirados resumos repetidos/contraditórios de CI, versão, INMET e prioridade da candidata; STATE e RDP ficam como referências de estado/fila. Arquitetura e navegação refletem os novos responsáveis.

Mantidos relatórios históricos, datasets, evidências, testes úteis, protocolos e scripts de reprodução. Um símbolo inicialmente sem referência na árvore de código era chamado pelos scripts científicos em docs: foi preservado. Os símbolos sem chamadas diretas restantes no inventário são handlers registrados por decorators. Nenhum arquivo de domínio/tools fingerprintado foi alterado. PDF acadêmico fora do escopo.

## Validação final

- Suíte principal: **651 testes backend**, warnings como erros, 66,59 s.
- Gate de hardening: **8 testes adicionais**, execução separada, 0,17 s.
- Frontend: **32 testes**, build/tipagem/ESLint; flags de variáveis/parâmetros sem uso aprovadas.
- Ruff em src/tests/docker; mypy Linux em **75 módulos**; actionlint; configurações Compose; gates de hardening, fronteira frontend, proxy e isolamento de carga aprovados.
- OpenAPI canônico **idêntico** ao HEAD `451d845` no mesmo ambiente Python: SHA-256 `dd96650a5d5b5157a1d49f095b21f10fbb7b2b337d74ca4183f30965f81c658f`. [Contrato](evidence/refatoracao-contrato-2026-10-20.json).
- Gitleaks: snapshot dos arquivos versionáveis, aproximadamente 17,56 MB, **zero achados**. Não equivale a nova varredura de histórico Git ou de diretórios privados/ignorados.
- API/frontend reconstruídos. Readiness e página inicial HTTP 200; previsão real de Belém HTTP 200, fonte Open-Meteo, dados completos/não obsoletos e política reference-v1.

[Registro de validação](evidence/refatoracao-validacao-2026-10-20.json). Tentativas Windows limitadas por tmpdir/sockets e AF_UNIX foram substituídas por verificações Linux; não contabilizadas como aprovações. CI remoto ainda não executado para o diff. Sem commit/push, merge ou release.

## Pendências de produto

A refatoração transversal solicitada está concluída neste lote. Permanecem no RDP acessibilidade auditiva, desenho/aceite científico, múltiplas fontes/modelos e uso comercial. Identidade de modelo/rodada no cache é evolução funcional própria da futura integração, não limpeza estrutural executada silenciosamente. Não há promessa de projeto livre de toda dívida técnica ou de produção homologada.
