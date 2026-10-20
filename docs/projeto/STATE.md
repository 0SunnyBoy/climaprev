# STATE — Clima Prev

## Estado vigente — 20/10/2026

- **Versão dos pacotes:** backend 0.1.0 e frontend 0.1.0; desenvolvimento local sem nova release/tag. Não confundir versão do pacote, identidade da política e versão de integração.
- **Git:** branch `develop`, atualização enviada em `edb81b0` e correções funcionais consolidadas em `f0eab5e`. Último lote funcional com CI e Security gates aprovados no mesmo SHA. Registro documental posterior não altera a aplicação; sem merge em main ou release.
- **Aplicação:** frontend Vue/TypeScript/Vite em `http://localhost:8080`, API FastAPI em `http://localhost:8000` e Redis local. Readiness e contratos HTTP/proxy foram verificados no lote atual; não existe ambiente de hospedagem definido.
- **Desacoplamento:** builds e Composes próprios para frontend e API; origem HTTP(S) configurada no build, CSP/CORS explícitos; modo integrado preservado. Gate HTTPS local entre origens distintas aprovado. Monorepo mantido.
- **Datas:** sete datas elegíveis, hoje UTC até +6, até sete dias consecutivos por consulta. API GET/POST valida antes do serviço; calendário atualiza na virada do dia/foco. Horizonte de 14 dias somente planejado.
- **Alertas:** validade/expiração reavaliadas na entrega e cache; interseção temporal no fuso local e geometria Polygon/MultiPolygon com furos; registros inválidos e formatos não suportados resultam em indisponibilidade conservadora. Identidade do adaptador `inmet-alerts-v2`, sem mudar a política `reference-v1`. INMET ao vivo não confirmado: HTTPX falhou com RemoteProtocolError e curl com conexão resetada/HTTP 000, sem prova da causa ou de indisponibilidade global.
- **Prazo:** orçamento cooperativo do serviço de consulta padrão 7 s, configurável até 8 s; cliente 10 s. Parsing/transporte/rate limit anteriores ao serviço ficam fora; cleanup pode ultrapassar o orçamento. Corrida de timers do cliente corrigida.
- **Interface:** contexto mantido após emergência, foco, busca por teclado/ARIA, tema/idioma persistidos e tradução reativa de erros; contraste de seis pares semânticos e layout 320–1280 px verificados automaticamente. Revisão manual com leitor de tela continua pendente.
- **Métricas:** exporter privado Prometheus, opt-in, com snapshots por worker em Redis (publicação 5 s, lease 20 s), histogramas e leitura limitada; dois workers reais verificados. Prometheus/Grafana/Alertmanager não instalados; templates não representam monitoramento operacional ativo.
- **Validação local:** 644 testes backend e 27 frontend aprovados, build/typecheck/ESLint/Ruff/mypy/actionlint aprovados; runtime UID 10001 sem testes/docs/env/ferramentas de desenvolvimento. Gate HTTPS de navegador com API real e upstream sintético aprovado. Acessibilidade automática não equivale a certificação WCAG.
- **Carga local:** cinco cenários de 60 s, dez usuários, aproximadamente dez req/s, 3.000 requisições sem falhas; maior p95 580 ms. Recursos limitados em Docker Desktop compartilhado e provedor sintético; não certifica capacidade de produção.
- **GitHub — qualificação funcional f0eab5e:** CI e Security gates concluídos com sucesso, incluindo Validate application, HTTPS independente, navegador/CSP, rotação sintética, scanner de imagem e regressão. As duas falhas de edb81b0 foram corrigidas sem relaxar CSP. Evidência em [aprovação dos gates](../operacoes/evidence/github-gates-aprovados-2026-10-20.json). develop sem proteção/checks obrigatórios; nenhuma regra administrativa alterada.
- **Ciência:** reference-v1 ativa, sem calibração/promoção. CSVs oficiais de três estações, baseline de cinco eventos, 72 snapshots espaciais, 3.747 casos catalogados e diagnóstico horário preparados. Resultados mistos, sem ganho substancial comprovado nem recuperação dos altos observados. Preparação mais completa não significa candidata superior.

## Prioridades e decisões vigentes

1. Confirmar acesso/contrato real dos avisos INMET, sem mascarar falha como ausência.
2. Correções enviadas e qualificação funcional aprovada em f0eab5e. Antes do merge, confirmar os checks do HEAD e revisar o diff final; merge depende de autorização própria. Acesso real INMET continua como limitação conhecida. Avaliar proteção/checks da develop com o proprietário; nenhuma regra foi alterada nesta revisão.
3. Consolidar revisão científica das fontes, semântica temporal, suficiência e proveniência das reservas, sem abrir novos outcomes ou ajustar política.
4. Fechar critérios de aprovação e nova versão prospectiva do protocolo com revisão científica: métrica/evento principal, suporte mínimo, ganho mínimo e tradeoffs ainda não aprovados.
5. Concluir revisão manual de acessibilidade com leitor de tela e registrar problemas e retestes.
6. **Por último:** retomar evolução da reference-candidate-1 com objetivo explícito de melhorar qualidade e precisão da previsão, comparando valores meteorológicos e detecção/falsos alarmes contra a v1 em dados independentes. Não basta reorganizar ferramentas ou mudar classificação. Fitting/calibração/promoção não autorizados nesta atualização.

A ordem acima corresponde às pendências 1, 2, 3, 4 e 6 da conversa; o item de evolução da candidata ficou para depois. Hospedagem/publicação operacional e provisionamento externo adiados pelo usuário. Monitoramento instalado e carga no ambiente definitivo dependem desse ambiente. Oferta da API a terceiros exige escopo próprio de autenticação/consumidores/quotas; separação de repositórios não solicitada. PDF acadêmico não deve ser atualizado.

## Evidências e navegação

[RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md) · [execução técnica](../operacoes/execucao-frentes-1-a-7-2026-10-20.md) · [estado GitHub](../operacoes/evidence/github-estado-2026-10-20.json) · [nova tentativa INMET](../operacoes/evidence/inmet-retomada-2026-10-20.json) · [diagnóstico científico](../planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md).

## Histórico

Os registros anteriores estão no [arquivo histórico](STATE-HISTORICO-ATE-2026-10-20.md). Eles não redefinem as prioridades ou o estado vigente.


[Estado atual dos protocolos científicos](../planejamento/reference-candidate-1/estado-dos-protocolos-2026-10-20.md): implementação técnica posterior e decisões ainda abertas, sem reescrever os originais congelados.
