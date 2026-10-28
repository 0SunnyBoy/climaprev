# RDP — 20/10/2026

## Continuidade mais recente da Frente 2 — 28/10/2026

Observações públicas das três estações obtidas até setembro/2026; Belém reconciliada por versão 2026 compatível com catálogo, sem alterar 2024. Interface recente do INMET exige reCAPTCHA e mostrou cota excedida; fonte pública verificada ainda não cobre outubro. Preflight pontual de cinco braços/três pontos concluiu 15/15; piloto recorrente segue desativado. Parser e comparador multivariável experimentais implementados para temperatura amostrada, umidade e rajada, com fonte/janelas/slot compatíveis e cobertura contra plano completo. Vento sustentado e extrema térmica sem previsão equivalente permanecem inelegíveis. **845 testes backend**, mypy **88 módulos**, Ruff/whitespace aprovados; sem frontend, fitting, incerteza nova, confirmação ou promoção. Ganho real da candidate-1 continua não demonstrado. Incremento local sem push/CI próprio. Relatório: `docs/operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md`; benefícios e condições: `docs/planejamento/reference-candidate-1/beneficios-esperados-candidate-1.md` (raiz). Este estado supera os bloqueios antigos de ausência total de CSV 2026/reconciliação de Belém, mas não a falta de dados atuais/equivalência instrumental.

## Preparação vigente da Frente 2 — 28/10/2026

Entregues verificação cadastral das três estações, diagnóstico observacional de 2024 conhecido, calendário desativado com rodadas explícitas, partições/allowlist e critérios conservadores por delegação. **826 testes backend completos**, mypy Linux em **86 módulos** e Ruff aprovados. Fonte atual do catálogo marca as três operantes; consultas de observações recentes retornaram 204 e não validam qualidade atual. A201 tem divergência de coordenadas entre catálogo e CSV histórico. Calendário de piloto 29/10–11/11, 18 UTC/15h Brasília, 210 jobs planejados; nenhuma rotina ativada. Partições de seleção/confirmação são condicionais e exigem congelamento antes das emissões; allowlist é classificação lógica, não movimentação ou bloqueio de arquivos no sistema operacional. Suporte efetivo e bloco temporal final continuam dependentes de dados antes da confirmação. Sem fitting, outcomes reservados novos, promoção, commit/push ou CI do incremento local. Ler `docs/operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). Preparação fechada; não declarar prontidão científica enquanto persistirem esses bloqueios. Registros abaixo são checkpoints anteriores onde conflitarem.

## Aceite delegado — 28/10/2026

Usuário delegou aceite de parâmetros fundamentados. Desenho aceito com condições: três estações iniciais, piloto técnico de 14 dias, referência de planejamento confirmatório de 12 meses após congelamento, confiança reportada de 95%, separação de dados e D+7 secundário exploratório. Metadados, calendário/rodadas, suporte, cobertura mínima e validade estatística ainda dependem de dados; margem de 0,5 mm, tolerâncias de cinco pontos percentuais e blocos de sete dias não são critérios confirmatórios validados. Não repetir pedidos rotineiros de aceite; documentar decisões e evidências. Sem ativação de campanha ou promoção e sem ampliar o escopo além das ordens 1 a 4. Registro: `docs/planejamento/reference-candidate-1/aceite-delegado-parametros-2026-10-28.md` (raiz). Este estado supera a pendência de aceite individual nos checkpoints abaixo, não suas limitações técnicas.

## Frente 2 — ordens 1 a 4 em 28/10/2026

Protocolo estruturado para revisão, contrato de chuva integrado ao pareamento, controle por estrato explícito (incluindo ausência da baseline em D+7) e avaliador diagnóstico de critérios sem limites padrão implementados. Critérios sem evidência suficiente retornam inconclusivo; não calculam intervalos nem autorizam promoção. Parâmetros científicos, instrumentação/antecedência e demais variáveis continuam pendentes. **815 testes backend completos**, mypy Linux em **85 módulos** e Ruff aprovados. Sem alteração do frontend, campanha, fitting ou promoção; reference-v1 ativa. Incremento local sem commit/push/CI próprio; 6576dd6 segue a base publicada aprovada. Rodada encerrada na ordem 4; ordens 5 a 9 não iniciadas por esta autorização. Relatório: `docs/operacoes/frente-2-ordens-1-a-4-2026-10-28.md` (raiz).

## Frente 2 iniciada — 27/10/2026

Protocolo consolidado para revisão e contratos de variáveis preparados em `docs/planejamento/reference-candidate-1/frente-2-protocolo-revisao-2026-10-27.md` (raiz). Novo diagnóstico isolado `experimental_equivalence` rejeita semântica, unidades, intervalos e valores incompatíveis. Ainda não ligado aos coletores/comparador, sem validar instrumentação, representatividade ou antecedência. 21 testes novos, Ruff e mypy do módulo aprovados; suíte integral histórica permanece checkpoint separado. Parâmetros e controle D+7 continuam propostas, campanha desativada e reference-v1 ativa. Incremento local sem commit/push. CI/Security publicados de `6576dd6` já aprovados; essa aprovação não cobre o novo diff.

## Qualificação remota e Actions — 27/10/2026

CI e Security do commit publicado `7b09fe6` concluídos com sucesso. A pendência de qualificação desse SHA está encerrada. Build do frontend reexecutada com Node.js 22.23.2 e aprovada; artefatos em frontend/dist. Avisos de Node 20 referem-se às ações do CI: atualização local de checkout/setup-node/upload-artifact para releases oficiais com node24 e runner fixado em Ubuntu 24.04. Atualização dos workflows incluída no envio autorizado para develop; conferir CI e Security do novo SHA antes de encerrar sua qualificação. Ver `docs/operacoes/atualizacao-actions-2026-10-27.md` a partir da raiz. Demais pendências científicas e de acessibilidade permanecem.

Atualização consolidada de 27/10: complemento de cobertura operacional qualificado com **757 testes backend**, mypy em **83 módulos** e Ruff; frontend com **48 testes**, lint/build e auditoria sem vulnerabilidades. Lote inicial publicado em `4525202`, Security gates aprovado; resultado remoto do complemento deve ser conferido no seu próprio SHA. Sem campanha ativa, promoção, merge em main ou deploy. Parâmetros continuam em revisão por escolha expressa do usuário. Registros numéricos anteriores são checkpoints históricos.

## Complemento de cobertura operacional — 27/10/2026

Lote consolidado publicado em `4525202`; CI e Security em acompanhamento, sem aprovação remota presumida. Adicionado diagnóstico somente leitura de jobs contra calendário explícito, inclusive slots inteiros ausentes e reservas vencidas; planos inativos não contam como falha. 43 testes direcionados, mypy do módulo e Ruff aprovados. Cobertura por alvo meteorológico/variável continua pendente. Usuário escolheu revisar parâmetros antes de aprovar; campanha segue desativada. Ver `docs/operacoes/consolidacao-2026-10-27.md` e `docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md` (caminhos a partir da raiz).

## Consolidação em 27/10/2026

Regressão integral local aprovada: **748 testes backend** (warnings como erros), mypy em **82 módulos**, Ruff e hardening local. O lote inclui coleta/comparação experimental, regressões dos avisos e melhoria da mensagem acessível de limite de requisições. Lockfile do frontend atualizado para corrigir os dois achados moderados do Vitest; auditoria após correção sem vulnerabilidades. Publicação e qualificação remota serão registradas no relatório desta consolidação.

Permanecem pendentes: teste auditivo real PT/EN; aceite dos parâmetros/calendário científicos e controle D+7; pareamento das demais variáveis; cobertura do calendário e incerteza estatística; coleta recorrente após aceite; refinamento e integração condicionados à evidência. Reference-v1 permanece ativa, sem campanha confirmatória iniciada ou ganho comprovado da candidate-1. Horizonte de 14 dias e hospedagem adiados.

## Comparação e elegibilidade em 26/10/2026

Comparador exploratório de chuva e entrada da baseline diária implementados, com cobertura, exclusões, identidade temporal, métricas e detecção diagnóstica por estação/horizonte de coleta. D+7 sem baseline aparece sem score; a definição do controle científico ainda precisa de decisão. [Entrega](docs/operacoes/comparacao-experimental-2026-10-26.md). 75 testes direcionados, tipagem e lint aprovados. Sem cálculo de novo ganho real ou campanha iniciada.

Continuam pendentes: parâmetros finais e controle científico de D+7; equivalência e pareamento das demais variáveis; cobertura global ligada ao calendário; intervalos de incerteza e avaliação independente; acionador recorrente após aceite; refinamento/promoção; teste auditivo; commit/push e CI do lote. Afirmações anteriores de ausência total de comparador foram superadas por este modo exploratório, não por um teste confirmatório completo.

## Verificação de avisos em 26/10/2026

Entrega das condições de chuva, vento, calor e frio verificada por cenários controlados da rota e componentes PT/EN; unidades do resumo corrigidas para °C/°F. 32 testes backend selecionados e 48 frontend, lint, tipagem e build aprovados. [Relatório](docs/operacoes/verificacao-avisos-2026-10-26.md). Não surgiu restrição que habilite apenas vento; causa da consulta original depende de cidade/período/dados. Teste auditivo, publicação do lote e pendências científicas permanecem. Sem alteração de limiares ou novo aviso de umidade.

## Atualização vigente de 26/10/2026

Concluído o incremento de baseline por adaptador/política, identidade de rodada explícita por Single Runs, manifesto versionado, orçamento/deduplicação SQLite local e pareamento exploratório de chuva com estação INMET. Runner por slot disponível, desativado; não há rotina recorrente instalada. **714 testes backend, 33 frontend, mypy 81 módulos, Ruff e hardening local aprovados.** [Relatório completo](RELATORIO-IMPLEMENTACAO-2026-10-26.md).

Pendências atuais: fechar e aprovar parâmetros/calendário e controle de D+7; definir elegibilidade por rodada e qualidade; preparar acionador operacional após aceite; parear outras variáveis com equivalência instrumental; comparar e refinar candidata em dados independentes; decidir integração após evidência. Acessibilidade auditiva e commit/push/CI do lote local também pendentes. Não reclassificar o replay exploratório de 2024 como prospectivo ou ganho comprovado. Os itens de baseline/manifesto/pareamento ausentes abaixo foram superados no escopo deste relatório, sem implantação.

## Coletores experimentais e preflight em 23/10/2026

- **Preflight pontual realizado:** GFS/IFS/ICON e MET Norway em Belém, Brasília e Porto Alegre; 11/12 combinações normalizadas. IFS/Porto Alegre rejeitado por chuva negativa, sem correção silenciosa. [Relatório](docs/operacoes/coleta-experimental-2026-10-23.md).
- **Coleta experimental implementada como CLI pontual**, com normalização de unidades/instantes e intervalos de chuva, escrita de arquivo bruto e rejeição de contratos inválidos. Não é agendador nem campanha confirmatória; rodada ainda desconhecida e nem todo horizonte possui dia local completo. Sem mudanças no endpoint público.
- **Validação:** 57 testes selecionados Docker, mypy de três módulos e Ruff aprovados. Sem suíte integral, commit/push ou CI remoto deste lote.
- **Próximos:** capturar baseline automática, comprovar rodada/disponibilidade, manifestos e orçamento de campanha, pareamento com observações e fechamento dos parâmetros propostos. Acessibilidade auditiva permanece pendente. Registros de ausência de HTTP/normalização abaixo são checkpoints anteriores.

## Incremento técnico de coleta em 23/10/2026

- **Etapa 3 avançada documentalmente:** catálogo GFS/IFS/ICON e MET Norway, restrições de acesso comercial, duplicação de origem e antecedência. Falta preflight dos campos/rodadas no endpoint; seleção final não foi inferida de desempenho. [Catálogo](docs/planejamento/reference-candidate-1/fontes-e-coleta-2026-10-23.md).
- **Etapa 4 iniciada:** arquivo experimental imutável de JSON/proveniência, separado por identidade e conteúdo, com proteção a sobrescrita, tempos UTC e sinalização de coleta tardia/rodada desconhecida. 34 testes selecionados Docker, mypy do módulo e Ruff aprovados. Ainda faltam adaptadores HTTP, envelope da baseline automática, normalização, agendamento e ligação às observações; não é coletor completo.
- **Parâmetros preparados para aceite:** [campanha proposta](docs/planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md), sem iniciar coleta ou abrir outcomes reservados. Datas, duração, margens e critérios pendentes permanecem propostas.
- Incrementos locais, sem novo commit/push ou CI remoto. Reference-v1 e janela pública de sete dias preservadas. Acessibilidade auditiva continua pendente.

## Atualização de 23/10/2026

**Direção científica aprovada pelo usuário**, após esclarecimento de que o protocolo inclui outras variáveis além da chuva. Objetivo inicial: chuva diária D+1; meta inicial: redução de MAE de pelo menos 5% com evidência favorável; avaliações complementares multivariáveis e D+3/D+7, teste independente e proteção dos extremos. [Registro e limites](docs/planejamento/reference-candidate-1/aprovacao-direcao-2026-10-23.md).

A pendência passa de revisão da direção para **fechamento dos parâmetros do experimento**: localidades/calendário/duração, semântica e qualidade das observações, diferença física relevante, margens dos extremos, suporte e plano estatístico. Segue seleção de fontes/modelos e preparação da coleta. Sem promoção, fitting ou leitura nova de outcomes reservados neste registro. Os checkpoints abaixo que dizem que a direção aguarda aprovação foram superados por esta decisão; demais pendências permanecem.

## Continuação vigente em 21/10/2026

Base publicada `5a6fc9c` aprovada no CI e Security gates. Registros abaixo que dizem "local sem push" ou citam `451d845` descrevem checkpoints superados dessa base, não a publicação atual. Incremento posterior permanece local, sem nova qualificação remota.

1. **Acessibilidade em andamento:** corrigida atualização a cada segundo da mensagem 429 na região de alerta; contador visual continua separado. Regressão no fluxo App e 33 testes frontend, lint, tipagem e build aprovados. Ensaio auditivo real continua pendente. [Detalhes e roteiro](docs/operacoes/acessibilidade-continuacao-2026-10-21.md).
2. **Protocolo científico aguardando revisão do usuário:** ele pediu a proposta detalhada antes de aprovar. [Documento preparado](docs/planejamento/reference-candidate-1/proposta-cientifica-para-revisao-2026-10-21.md), com alternativas de alvo, comparadores, cobertura, partição temporal, métricas e decisões quantitativas ainda pendentes. Não presumir aprovação de 5%, objetivo, reservas ou promoção.
3. **Próximos:** seleção de fontes/modelos, coleta experimental, comparação observacional, refinamento e integração condicionada. Desenho da campanha depende das escolhas do item 2; pesquisa de fornecedores e preparação técnica independentes podem avançar sem abrir outcomes de teste.

## Revisão vigente — aplicação e análise com múltiplas fontes

Revisão posterior de linhas concluída: 109 linhas retiradas sem excluir testes; 18.299 no escopo contado, ainda +195 contra o commit (+168 testes/gates, +27 executável). Mapeamento e wrappers simplificados; 659 testes backend, 32 frontend, checks estáticos/build e equivalência de contrato aprovados. [Detalhamento](docs/operacoes/reducao-linhas-2026-10-20.md).

Refatoração estrutural implementada: prazos/cancelamento compartilhados, DTOs/conversões e codecs fora do serviço, schemas fora da rota, tipagem concreta e imports limpos. Contrato OpenAPI preservado; 651 testes da suíte principal, oito adicionais de hardening, 32 frontend, build/lint/tipagem e gates locais aprovados na refatoração transversal. [Execução e limites](docs/operacoes/refatoracao-2026-10-20.md). A avaliação arquitetural anterior permanece como diagnóstico histórico; cache/locks/avisos também foram separados em serviços próprios neste lote transversal; main, testes, frontend, configuração e documentação corrente foram revisados.


**Etapa 1 concluída no escopo local:** busca com prazo de cinco segundos e consulta principal com encerramento independente do abort em dez segundos; regressão de transporte travado/cancelamento/resposta tardia, medição controlada fria/repetida em três cidades e falhas injetadas, revisão no navegador de 320–1280 px e consulta real de sete dias. 31 testes frontend e 34 testes backend selecionados aprovados. Não é certificação de produção ou disponibilidade dos provedores. [Relatório e limitações](docs/operacoes/responsividade-2026-10-20.md). Leitor de tela é etapa 2 ainda pendente; segue preparação da etapa 3. Novas mudanças locais, sem commit/push. Este estado substitui o primeiro incremento abaixo.


Esta seção substitui a ordem e as afirmações conflitantes do checkpoint abaixo. O usuário retomou a candidate-1 e definiu foco em responsividade, qualidade e velocidade, priorizando a aplicação. O objetivo futuro é código aberto com possibilidade de serviços empresariais pagos e apoio da comunidade. Novas integrações são planejamento; nenhum provedor ou combinação foi implementado nesta revisão.

Git local: `develop`, HEAD e referência local `origin/develop` em `451d845`. O lote INMET/busca foi commitado e enviado anteriormente. Os checks desse SHA não foram consultados novamente nesta revisão; aprovações de SHAs anteriores não o qualificam automaticamente. Última validação registrada: 651 testes backend e 28 frontend, build/lint/tipagem aprovados; não reexecutados nesta revisão documental. Reference-v1 permanece ativa, sem ganho superior comprovado da candidata.

| Ordem | Implementação ou decisão pendente | Entrega / critério de conclusão |
|---|---|---|
| 1 — concluída localmente | Responsividade e desempenho real da aplicação | Recuperação corrigida e medições/revisão responsiva registradas no relatório. Sem afirmar causa universal de timeouts anteriores, capacidade de produção ou ganho de latência do backend. Acompanhamento dos provedores continua operacional |
| 2 | Concluir acessibilidade | Realizar ensaio auditivo com leitor de tela em PT/EN, corrigir e retestar. Teclado/inspeção no Edge já parciais; usuário informou que não pode executar o ensaio agora |
| 3 | Fechar desenho científico da candidate-1 | Deliberar sobre revisão preparada, equivalência das variáveis, independência das reservas, métrica/evento principal, ganho mínimo, tolerâncias e suporte. Usuário responsável pelo aceite; critérios ainda não aprovados. Registrar protocolo novo sem alterar originais congelados |
| 4 | Selecionar fontes/modelos e condições de uso | Priorizar GFS/ECMWF/ICON pela Open-Meteo e avaliar MET Norway como segundo provedor. Conferir cobertura brasileira, campos, intervalos, histórico, limites, atribuição e uso comercial. ECMWF direto fica como alternativa de maior custo técnico. Registrar modelo de origem para evitar contar duplicações como evidência independente |
| 5 | Implementar coleta experimental e normalização | Adaptadores substituíveis; registrar rodada, antecedência, coordenadas, fuso, unidade, intervalo, atualização e versão. Cache separado por modelo/provedor/rodada, falhas explícitas e controles HTTP reaproveitados. Preferir coleta em segundo plano para não alongar cada consulta. Falta de campo não vira zero nem é preenchida silenciosamente |
| 6 | Comparar modelos com observações | Avaliar D+1/D+3/D+7 por variável/local, extremos e falsos alarmes; dados INMET reconciliados como referência observacional, reanálise apenas como controle. Usar desenho temporal aprovado e preservar teste independente; documentar lacunas de histórico |
| 7 | Desenvolver refinamento da candidata | Testar correções e combinações contra cada modelo individual e a baseline v1. Ajustar pesos apenas em desenvolvimento; medir ganho fora da amostra e regressões. Concordância não equivale a probabilidade calibrada; média simples pode apagar extremos |
| 8 | Integrar candidata qualificada à aplicação | Somente após evidência e aceite: identidade/versionamento próprios, rastreabilidade de fontes, tratamento de divergências/dados parciais, testes de contrato, latência e regressão. Promoção não automática; avisos oficiais permanecem distintos do risco calculado |
| 9 | Preparar distribuição aberta e oferta de serviços | Definir licença do código, créditos e termos dos dados; documentar configuração comunitária/comercial sem credenciais no repositório. Para serviço empresarial: escopo de consumidores, autenticação, quotas, suporte e versionamento de contrato. Não separar repositórios neste momento |
| Transversal | Qualificação das entregas | Atualizar documentos do projeto/RDP, verificar CI e Security gates do HEAD e revisar mudanças antes de merge. Não implica autorização de merge em main ou implantação |

### Fontes e receita — condições verificadas em 20/10/2026

- [Open-Meteo](https://open-meteo.com/en/terms): serviço gratuito não comercial, com cotas; doações voluntárias são permitidas. Integrações pagas, publicidade e atividades promocionais exigem enquadramento comercial. Crowdfunding precisa ser classificado pelo formato e contrapartidas; não equivale automaticamente a doação. Dados CC BY 4.0 e acesso ao serviço são condições distintas.
- [MET Norway — licença](https://api.met.no/doc/License) e [termos](https://api.met.no/doc/TermsOfService): dados abertos com atribuição, identificação da aplicação e uso responsável; sem SLA. Verificar exceções do produto. Fonte global ECMWF e ausência de histórico global no Locationforecast limitam independência e avaliação retrospectiva: [modelo de dados](https://docs.api.met.no/doc/locationforecast/datamodel.html).
- [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data): uso comercial e redistribuição com atribuição e cumprimento dos termos; ingestão direta exige processamento adicional.
- APIs públicas sem chave continuam exigindo validação de contrato/dados, limites, timeout, tamanho de resposta e tratamento seguro de falhas. Código aberto não elimina obrigações do serviço utilizado.

Continuam adiados: horizonte de 14 dias (apenas planejado), hospedagem/monitoramento no ambiente definitivo e separação de repositórios. Acesso real INMET já verificado em amostra controlada; resta acompanhar disponibilidade/cobertura, não repetir o diagnóstico como se o acesso ainda estivesse bloqueado. PDF acadêmico fora do escopo.


## Operação futura e histórico

Monitoramento: exporter e templates existentes; instalar serviços, alertas, retenção e SLOs no ambiente futuro. Capacidade/uptime exigem ensaio nesse ambiente. develop permanece sem proteção obrigatória registrada; revisar checks do HEAD antes de merge, sem alterar regras administrativas neste lote. Relatórios anteriores e protocolos preservados: [frentes 1–4](docs/operacoes/frentes-1-a-4-2026-10-20.md), [frentes 1–7](docs/operacoes/execucao-frentes-1-a-7-2026-10-20.md), [RDP anterior](RELATORIO-PENDENCIAS-2026-10-19.md). Resumos repetidos e desatualizados do documento vigente foram consolidados; evidências não foram removidas.
