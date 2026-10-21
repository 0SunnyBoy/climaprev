# RDP — 20/10/2026

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
