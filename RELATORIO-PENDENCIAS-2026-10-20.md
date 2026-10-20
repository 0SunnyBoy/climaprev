# RDP — 20/10/2026

## Incremento local posterior ao checkpoint remoto c5408a0

INMET real agora verificado em amostra controlada, inclusive de dentro do Docker, após identificação explícita no User-Agent; bugs de repetição por teclado e resposta vazia da geocodificação corrigidos. Previsão real recebida no Edge após um timeout e repetição controlada. Revisão preparatória e critérios concretos prontos para o aceite do usuário, que confirmou ser o responsável. Inspeção interativa no Edge concluída parcialmente; ensaio auditivo com leitor de tela pendente. Validação atual: **651 backend e 28 frontend**, build/tipagem/lint aprovados. Este incremento ainda não foi enviado; aprovação remota de c5408a0 não cobre o diff local. [Relatório completo](docs/operacoes/frentes-1-a-4-2026-10-20.md).

A ordem restante passa a ser: aceite da revisão/fontes/proveniência; definição e aprovação das escolhas quantitativas; leitor de tela e cenários de resultado; revisão/envio do novo lote e CI. INMET sai da condição de acesso não confirmado, mas permanece sujeito a acompanhamento de disponibilidade e cobertura. As tabelas abaixo registram o checkpoint anterior quando conflitarem com este incremento.

## Versão e situação da aplicação

Backend e frontend **0.1.0 em desenvolvimento**, branch `develop`, base `23bf4ce`, atualizada no GitHub em `edb81b0`, sem merge em main ou nova release; correções funcionais qualificadas em f0eab5e com CI e Security gates aprovados. Aplicação funciona localmente com Docker, API, frontend e Redis. Estado detalhado e evidências em [STATE](docs/projeto/STATE.md).

## Implementações concluídas no escopo local

| Área | Entrega | Limite atual |
|---|---|---|
| Desacoplamento | Builds/Composes independentes, API origin, CSP/CORS e gate HTTPS | Monorepo preservado; sem hospedagem externa |
| Datas/fusos | Janela pública hoje UTC até +6; API/calendário sincronizados | 14 dias somente planejado |
| Alertas | Validade, expiração/cache, intervalo local, Polygon/MultiPolygon/furos e falha conservadora | Acesso ao INMET real ainda não homologado |
| Consulta | Prazo cooperativo padrão 7 s, máximo 8 s, cleanup e timer do cliente corrigido | Não é limite absoluto de transporte/cleanup |
| Interface | Contexto/foco após emergência, teclado/ARIA, tema/idioma, erros reativos e responsividade | Leitor de tela manual pendente |
| CI | Lint/testes/build/tipagem/auditoria, Composes, runtime e gate HTTPS configurados | CI e Security gates aprovados em f0eab5e; sem deploy |
| Observabilidade | Exporter privado por worker, Redis temporário e histogramas; templates | Serviços de monitoramento não instalados |
| Carga | 3.000 requisições, cinco cenários, zero falhas, cerca de dez req/s; maior p95 580 ms | Bancada local sintética, sem certificação de produção |
| Preparação científica | CSVs, bootstrap, baseline, comparação espacial, catálogo e diagnóstico horário | Sem aprovação científica ou ganho substancial comprovado |

Última validação: **644 testes backend e 27 frontend aprovados**, build/typecheck/ESLint/Ruff/mypy/actionlint, imagem runtime UID 10001 e gate HTTPS local aprovados. [Relatório e limites](docs/operacoes/execucao-frentes-1-a-7-2026-10-20.md).

## Pendências prioritárias — ordem vigente

| Prioridade | Pendência | Próxima ação / critério de conclusão |
|---|---|---|
| 1 | Avisos INMET reais | Diagnosticar resets/RemoteProtocolError, confirmar origem/contrato e validar avisos reais. HTTP 000 não é ausência de avisos; causa ainda desconhecida |
| 2 | CI remota — concluída para o lote funcional | CI e Security gates aprovados em f0eab5e. Confirmar checks do HEAD antes de merge; publicação do código não é deploy |
| 3 | Revisão científica preparatória | Revisar fontes, convenções temporais, comparabilidade, suporte raro e proveniência/independência das reservas; registrar conclusão e limitações |
| 4 | Critérios de aprovação | Fechar evento/métrica principal, suporte/ganho mínimo, tradeoffs, multiplicidade, revisor e protocolo prospectivo antes de ajuste; não inventar aceite |
| 6 da lista original | Acessibilidade manual | Testar leitor de tela, teclado, foco, erros, resultados e emergência em PT/EN; registrar ambiente e achados, corrigir e retestar |

**Estado remoto confirmado:** CI e Security gates aprovados no mesmo commit funcional `f0eab5e`, após corrigir o nome da imagem da bancada e a asserção de tema incompatível com CSP. Qualificação funcional para merge concluída, sem realizar o merge. Revisão do diff e checks do HEAD continuam necessários antes de integrar. [Evidência](docs/operacoes/evidence/github-gates-aprovados-2026-10-20.json). develop permanece sem proteção/checks obrigatórios; nenhuma regra administrativa modificada.

## Evolução da candidata — por último

Por orientação do usuário, a evolução da **reference-candidate-1** fica após as pendências prioritárias. Quando retomada, o objetivo será melhoria mensurável de **qualidade e precisão da previsão** em relação à reference-v1, com avaliação meteorológica e de classificação separadas, detecção de extremos, falsos alarmes e incerteza. Os experimentos atuais são preparação/diagnóstico, não uma candidata calibrada superior. Reference-v1 ativa; nenhum fitting, calibração ou promoção autorizado/executado nesta atualização. Itens 3 e 4 acima são preparação e revisão, não autorização de ajuste.

## Adiados ou condicionais

- **Hospedagem/publicação:** adiada explicitamente; não há servidor/domínio preparado. DNS/TLS público, segredos reais, rollout/rollback e operação ficam para a retomada dessa frente.
- **Monitoramento operacional:** instalar Prometheus/Grafana/Alertmanager, retenção, destinos de alertas, responsáveis e SLOs no ambiente futuro; templates e exporter não encerram isso.
- **Capacidade:** ensaio sustentado no ambiente definitivo; resultados locais não estimam capacidade máxima nem disponibilidade real dos provedores.
- **API comercial/terceiros:** autenticação, consumidores, quotas e suporte dependem de definição do produto. Contratos Python/TypeScript ainda mantidos separadamente.
- **Repositórios:** separação não solicitada; componentes já executam separadamente no monorepo.

## Horizonte de 14 dias — somente planejado

Disponibilizar futuramente 14 datas elegíveis, contando hoje, mantendo até sete dias consecutivos por consulta. Não ativado por orientação do usuário. Exigirá API/calendário coerentes, cobertura e qualidade das variáveis até o último dia, identificação da incerteza da segunda semana, revisão de contrato/mensagens/cache/limites e testes de fronteira/fuso. Avaliação D+14 requer desenho próprio: os experimentos atuais D+1/D+3/D+7 não a validam. Não mudar limiares ou calibração automaticamente.

## Histórico e rastreabilidade

[Datas/fusos](docs/arquitetura/datas-e-fusos-2026-10-20.md) · [desacoplamento](docs/arquitetura/desacoplamento-2026-10-20.md) · [diagnóstico científico](docs/planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md) · [RDP anterior](RELATORIO-PENDENCIAS-2026-10-19.md). Protocolos congelados, evidências e resultados históricos preservados; PDF acadêmico fora do escopo.
