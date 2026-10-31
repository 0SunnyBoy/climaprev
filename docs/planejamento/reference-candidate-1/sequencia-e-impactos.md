# reference-candidate-1 — sequência de execução e impactos

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Prioridade revista — 20/10/2026

A evolução da candidate-1 foi adiada pelo usuário para depois de INMET real, CI remota, revisão científica preparatória, critérios de aprovação e acessibilidade manual. Quando retomada, o objetivo explícito será qualidade e precisão da previsão, com comparação meteorológica e de classificação contra v1, extremos/falsos alarmes e incerteza. Preparação de ferramentas não conta como ganho preditivo. A/B/AB abaixo permanecem propostas históricas, sem autorização de fitting/calibração/promoção. [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).

Data: 16/10/2026, America/Sao_Paulo. Referência: develop@23bf4ce. Estado: planejamento proposto, sem implementação de política/calibração.

Atualização em 16/10: o primeiro lote de infraestrutura e diagnóstico foi executado após a redação deste plano. Consulte `execucao-2026-10-16.md`; a política ativa continua v1, e nenhum ajuste científico ou promoção foi aprovado.

## Direção recomendada

Preservar o comportamento da reference-v1 como baseline reproduzível. Evoluir a infraestrutura que permite escolher políticas e executar uma candidata identificada separadamente. Mudanças em regras/limiares que alterem resultados precisam de nova identidade; reorganizações internas comprovadamente sem mudança de comportamento podem manter a identidade da v1.

Uma correção de defeito que altere a classificação também precisa de rastreabilidade de comportamento/versão e comparação com o resultado anterior. Não corrigir silenciosamente a baseline histórica nem reescrever resultados já registrados.

O programa terá dois experimentos e uma avaliação combinada, com coleta, qualidade, fontes observadas e ferramentas compartilhadas. Preparar os dois não exige ajustar ambos ao mesmo tempo.

| Configuração | Previsão | Política | Pergunta |
| --- | --- | --- | --- |
| R0 — baseline | Original | V1 congelada | Qual é o desempenho atual? |
| A — política | Original | Candidata | As novas regras melhoram a classificação? |
| B — calibração | Corrigida por perfil experimental | V1 congelada | A correção melhora os valores previstos e seus efeitos na classificação? |
| AB — combinação | Corrigida | Candidata | A combinação acrescenta ganho e preserva os critérios de segurança? |

Configurações A/B/AB usam a mesma referência observada e, para comparação direta, a mesma população elegível. Limiares, perfil e decisões de combinação são escolhidos sem consultar o conjunto final reservado. Ganho de MAE/RMSE não implica automaticamente redução de omissões de eventos, e ganho de classificação não comprova melhoria dos valores meteorológicos.

## Melhor sequência de execução

| Ordem | Entrega | O que executar | Condição para seguir |
| --- | --- | --- | --- |
| 1 | Protocolo e baseline congelada | Registrar versão/código, regras, dataset-alvo, localidades, eventos, fontes, splits e metas de aceite | Critérios e alvos definidos antes de escolher ajustes |
| 2 | Base de dados e qualidade | Completar CLI existente: proveniência, entradas salvas, cobertura horária por variável/fuso, exclusões, unidades, retomada e execução sem rede sobre entradas salvas | Dados elegíveis e reproduzíveis; comparação temporal coerente |
| 3 | Referência observada e comparador | Congelar rótulos; distinguir observação meteorológica, reanálise e impacto; implementar métricas por evento/classe/antecedência e incerteza | Mesmo alvo para todas as opções; contagens e denominadores testados |
| 4 | Diagnóstico R0 | Executar v1 nos dados elegíveis, com valores originais; medir classificação e erros meteorológicos, sazonalidade e cobertura | Identificar onde há erro tratável e amostra suficiente |
| 5 | Suporte experimental e ajustes A/B | Versionar política/perfis, validar configurações e ajustar separadamente nas partições de ajuste/validação | V1 preservada, alterações justificadas; sem acesso ao teste final |
| 6 | Combinação e teste reservado | Definir previamente A/B/AB a avaliar; comparar no teste final pareado, com estratos e deltas | Metas atendidas, limitações e regressões explícitas; evidência insuficiente mantém estudo aberto |
| 7 | Revisão e decisão | Revisão meteorológica/produto; selecionar manter v1, promover uma configuração ou ampliar estudo | Parecer, escopo geográfico/temporal e versão da configuração registrados |
| 8 | Integração, gates e promoção | Seleção explícita no backend, proveniência na resposta quando necessária, contratos/UI/documentos, monitoramento e rollback | Testes/gates da versão final e retorno à configuração anterior verificados |

Depois do diagnóstico, executar primeiro o ajuste mais sustentado pelos dados. Se a principal causa estiver nos valores meteorológicos, priorizar B. Se os valores estiverem adequados e as regras omitirem eventos/falharem na classificação, priorizar A. Não escolher limiares novos apenas porque há espaço para configurá-los.

Na etapa 6, o teste reservado serve para avaliação e decisão de promoção, não para buscar novos parâmetros. Se houver ajustes após abrir esse teste, é necessária nova avaliação independente. Episódios, datas válidas e antecedências devem respeitar a separação temporal para evitar vazamento.

Partes da infraestrutura de versionamento e comparador podem avançar enquanto se auditam as fontes. A falha de tema e os checks frontend devem ser resolvidos em paralelo para permitir o aceite final; o estudo offline não depende de esperar toda a implantação pública. Segurança, homologação, monitoramento e rollback tornam-se gates na etapa 8.

As metas numéricas, períodos, tamanho suficiente da amostra, fontes finais de rótulos e revisor ainda precisam ser definidos. Isso não impede preparar ferramentas, mas impede declarar ganho científico ou promoção concluídos.

## Se alterarmos a reference-v1, o que mais muda?

Há três situações diferentes:

1. Preparar suporte a candidatas, preservando resultados da v1: muda a infraestrutura de políticas e testes; a baseline continua com a mesma identidade.
2. Mudar limiares/regras e, portanto, resultados: a configuração alterada ganha identidade experimental própria; não continua sendo chamada silenciosamente de v1.
3. Mudar os dados de entrada ou corrigi-los: além da política, revisar modelo de dados, normalização, completude, cache e proveniência, conforme o alcance da mudança.

## Mapa de impactos confirmado no código

| Área | Arquivos principais | Necessário / condicionado |
| --- | --- | --- |
| Política | src/climaprev/domain/risk_policy.py | Identidade explícita para candidata; validação de finitude e ordem dos limiares; defaults/identidade histórica v1 preservados |
| Cálculo | src/climaprev/domain/risk_evaluator.py | Alterar quando mudarem regras, agregação ou condições; novos valores de limiar podem usar o avaliador atual, com testes de fronteira |
| Avaliação histórica | src/climaprev/tools/validate_historical.py; src/climaprev/domain/risk_validation.py | Seleção experimental, rótulos fixos, qualidade/proveniência e relatórios comparativos; não gerar o alvo usando a candidata em avaliação |
| Composição/configuração | src/climaprev/main.py; src/climaprev/config.py; exemplos/Compose se introduzirem opções | Na integração: seleção explícita por configuração confiável, validação no startup, default e rollback documentados; hoje main cria RiskPolicy() diretamente |
| Orquestração | src/climaprev/application/services/forecast_query.py; src/climaprev/application/ports.py | Rever injeção/contrato apenas quando necessário; preservar avaliação diária, picos, conversão de unidades e prioridade INMET |
| API | src/climaprev/api/routes/risk.py; src/climaprev/domain/models.py | policy_version já é string e propagada; testar a versão selecionada. Atualizar schemas se acrescentarem metadados, condições, níveis ou unidades |
| Frontend | frontend/src/types/api.ts; services/api.ts; components/ForecastResult.vue; components/RiskSummary.vue; composables/useLocale.ts | Uma nova string de versão já é aceita/exibida. Novos campos, tipos de condição, unidades ou explicações exigem adequação de parser, tipos, apresentação e textos PT/EN |
| Qualidade/variáveis | domain/models.py; domain/data_quality.py; infrastructure/providers/open_meteo.py; coletor histórico | Necessário se novas regras usarem variáveis hoje ausentes ou não exigidas para completude; alinhar disponibilidade, unidades, cobertura e contratos |
| Calibração | domain/bias_correction.py; composição/serviço | Se promovida B/AB: perfil/coefs imutáveis e rastreáveis, ativação explícita, compatibilidade com dados/escopo e fallback |
| Cache | application/services/forecast_query.py; testes de identidade/expiração/cache | Só limiares: cache meteorológico pode ser reutilizado, risco é recalculado. Calibração: perfil já participa da chave. Mudança estrutural/normalização: revisar serialização e versão da chave |
| Métricas/logs | api/observability.py; métricas e runbooks | Métrica já separa policy_version; verificar identificação da configuração/calibração em operação e evitar versões arbitrárias de alta cardinalidade |
| Testes | tests/unit/domain; unit/tools; integration/application; integration/api; frontend; tests/docker | Preservar testes de v1 e acrescentar candidata/calibração/rollback; validar backend e UI nos contratos afetados |
| Documentação | README; docs/arquitetura; docs/operacoes; docs/projeto; planejamento | Atualizar limiares e escopo, metodologia, política ativa, limitações, proveniência, comandos, rollout/rollback e resultados |
| Pacote de contexto | manifestos/índices/relatórios futuros | Gerar evidência correspondente ao commit final; preservar pacotes anteriores como históricos |

## Detalhes que evitam mudanças desnecessárias ou incorretas

### Versão da política não é método de avaliação

`method` atualmente é forecast_heuristic. `policy_version` identifica as regras, por exemplo reference-v1 ou uma candidata. São informações diferentes. Fixtures em `frontend/src/services/api.test.ts` e `tests/docker/check_frontend_browser.py` usam reference-v1 também como method; devem ser alinhadas ao contrato real quando esses testes forem trabalhados. Não copiar essa confusão para a candidata.

### Não substituir todas as ocorrências de reference-v1

Testes, baselines e documentos históricos precisam continuar identificando a v1. Atualizar o estado ativo e adicionar cobertura da nova configuração; não fazer substituição global que apague evidência do fallback.

### API e UI já têm suporte parcial

O schema backend usa policy_version como string. O frontend também aceita string e `ForecastResult.vue` mostra a versão. Trocar apenas a identidade não exige uma nova rota ou redesign. Mesmo assim, testar GET/POST, daily, peak_days e risk_overview com a configuração escolhida.

Novas condições/regras podem exigir explicações novas: o frontend tem rótulos e razões inglesas mapeados por tipo. Se uma regra passar a depender de duração, região ou outra variável, verificar que PT/EN descrevem esse motivo corretamente. Campos novos ou mudança dos níveis low/moderate/high exigem análise de compatibilidade em todos os consumidores.

### Proveniência se a previsão for calibrada

A resposta atual informa provedor e fetched_at, mas não expõe perfil/versão de calibração. Ao promover B/AB, definir metadados suficientes para distinguir valor original de corrigido, mantendo a fonte meteorológica identificada. Isso pode exigir evolução aditiva dos schemas, tipos/parser e seção de metodologia da UI. A forma exata do contrato será definida antes da integração.

### Cache e modelo de dados

Hoje a previsão normalizada é recuperada do cache e então avaliada com a política injetada. Uma mudança só de política não exige apagar Redis, mudar chave de geocodificação ou invalidar alertas INMET. Se um resultado de risco vier a ser cacheado, sua chave precisará identificar a política.

Se mudar calibração, cada conjunto de coeficientes deve ter nova identidade de perfil; trocar números mantendo o mesmo ID poderia reaproveitar valores antigos. Se mudar a estrutura das variáveis/normalização, revisar leitura e escrita do cache e sua versão; não remover valores em massa como solução padrão.

### Fallback é uma configuração completa

Identificar a combinação política + perfil de calibração + versão de normalização no artefato de publicação. O rollback para a baseline deste estudo retorna à v1 com perfil disabled. Trocar apenas a política deixando um perfil experimental ativo não reproduz a baseline original.

### Fontes e horizonte

Mudar política não aumenta automaticamente o suporte temporal do provedor ou da API. Se houver objetivo de ampliar sete dias, é uma frente adicional: schema/formulário, provedor, disponibilidade, quotas, cache, validação por antecedência e documentação.

## Primeiro lote recomendado de implementação

1. Fechar o contrato mínimo do experimento: população, fonte/definição do alvo, divisão temporal e critérios prévios.
2. Preparar coleta/normalização com cobertura, exclusões e entradas reproduzíveis.
3. Implementar comparador de classificação e erros meteorológicos com referência fixa.
4. Registrar baseline da v1 nos dados elegíveis.

A identidade/validação das candidatas pode ser preparada junto desse lote, sem alterar o comportamento da API. Novos limiares e coeficientes só serão escolhidos após o diagnóstico. A especificação detalhada está em `analise-e-plano.md`.

## Critério de conclusão do programa

O trabalho termina com decisão documentada e reproduzível: manter baseline, promover A, promover B ou promover AB, dentro do escopo em que a evidência é suficiente. Promoção requer revisão, testes/gates da configuração final, comunicação coerente, monitoramento e rollback demonstrado. Resultado inconclusivo mantém a configuração experimental fora da produção.

Esta entrega atualiza somente o planejamento. Nenhuma regra, limiar, coeficiente, contrato público ou configuração ativa foi alterado.
