# Especificação — evolução do Clima Prev

**Estado:** Approved para execução local por solicitação do usuário em 2026-09-13.
**Contexto:** [context.md](context.md). **Design:** [design.md](design.md).
Os marcadores WHEN/IF/THEN/SHALL formalizam critérios verificáveis; SHALL
significa “deve”. IDs identificam requisitos, não funcionalidades já entregues.

## Problem Statement

A API existente permite consultar risco climático, mas o fuso retornado pode
divergir da previsão, o stale pode expirar durante uma espera e dados
incompletos podem parecer uma avaliação completa. Falhas externas, configuração,
logs e implantação também precisam de contratos mais precisos.
O usuário final ainda não dispõe de uma interface de consulta.

## Goals

- [ ] Fornecer local, período, unidades e qualidade coerentes em todas as respostas.
- [ ] Impedir entrega de cache expirado e erros internos para falhas previstas.
- [ ] Tornar os controles de operação verificáveis em ambiente local isolado.
- [ ] Entregar uma interface de consulta que comunique limitações corretamente.

## Out of Scope

| Item                                                        | Motivo                                                                       |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Implantação pública, domínio ou contratação cloud           | O pedido atual é de planejamento; fornecedor e ambiente ainda não definidos. |
| Contas, favoritos, histórico e notificações                 | Exigem contratos de identidade e dados próprios.                             |
| Integração real de alertas oficiais                         | Fonte e cobertura não escolhidas.                                            |
| Alterar limiares de risco ou introduzir ML                  | Não há validação científica nova para mudar a política.                      |
| Migração para microserviços, SIGFAS, Keycloak ou PostgreSQL | Não é necessária para os objetivos deste ciclo.                              |

## Assumptions & Open Questions

| Assumption / decision | Chosen default                                                                               | Rationale                                                     | Confirmed?                                |
| --------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------- |
| Contrato HTTP         | Campos atuais preservados; qualidade aditiva.                                                | Evitar quebra dos consumidores atuais.                        | Premissa técnica.                         |
| Risco com lacunas     | `complete`, `partial` ou `unavailable` em `data_quality.completeness`.                       | Exibir lacunas sem mudar níveis da política.                  | Premissa de produto.                      |
| Interface             | HTML/CSS/JS sem framework, na mesma origem.                                                  | Minimizar dependências para o primeiro fluxo.                 | Premissa técnica.                         |
| Autenticação          | Consulta anônima, sem operações pessoais.                                                    | Compatível com a base e o escopo.                             | Premissa de produto.                      |
| Calendário permitido  | Até sete dias inclusivos; datas indisponíveis no provedor viram erro externo sanitizado.     | Não inventar horizonte fixo do provedor.                      | Premissa técnica.                         |
| Cota global           | Token bucket configurável por ambiente/provedor; valor obrigatório em homologação protegida. | O orçamento real ainda precisa ser definido pelo operador.    | Valor real pendente; testes usam fixture. |
| Logs                  | Somente metadados sanitizados; retenção de sete dias na homologação proposta.                | Limite explícito e revisável antes de publicar.               | Premissa operacional.                     |
| Telemetria            | Snapshot JSON por processo em rota interna; não prometer agregação global.                   | Reutilizar coletor existente sem escolher plataforma externa. | Premissa técnica.                         |

**Open questions: none** sem tratamento: todas as ambiguidades estão
registradas acima como premissas ou no backlog fora do escopo. Isso não
significa aprovação das premissas nem definição de valores de produção.

## User Stories

### P1: Receber previsão coerente e com qualidade explícita

**User Story:** Como consumidor, quero saber o local, o fuso e as limitações
dos dados para interpretar a previsão sem confundir lacunas com segurança.

**Acceptance Criteria:**

1. WHEN o provedor responder com um fuso IANA válido THEN a API SHALL devolver esse fuso em `location.timezone`, tanto em consulta por texto quanto por coordenadas, inclusive em cache hit. **DAT-01**.
2. IF um valor meteorológico for não finito, percentual fora de 0–100, chuva/vento negativos ou mínima maior que máxima THEN a API SHALL responder 502 `WEATHER_DATA_INVALID`. **DAT-02**.
3. WHEN os dados usados na política forem avaliados THEN a API SHALL classificar a completude como `complete`, `partial` ou `unavailable` pela tabela normativa abaixo. **DAT-03**.
4. WHEN houver amostras horárias válidas de temperatura THEN o adaptador SHALL calcular `temperature_mean` pela média das amostras não nulas do dia; sem amostras, o valor será `null`. **DAT-04**.
5. IF dois locais diferirem nas coordenadas efetivas THEN o cache SHALL impedir que a previsão de um seja servida como previsão do outro. **CON-01**.

**Independent Test:** Consultas por texto e coordenadas com fixtures de fuso,
dados completos, nulos, fora de faixa e pontos separados por menos de 0,0001°.

### P1: Recuperar falhas sem usar previsão vencida

**User Story:** Como consumidor, quero respostas previsíveis quando a
previsão, o Redis ou outra atualização estiverem indisponíveis.

**Acceptance Criteria:**

1. IF o relógio atingir `stale_until` antes da entrega do fallback THEN o serviço SHALL recusar essa entrada e retornar 503 `WEATHER_PROVIDER_UNAVAILABLE`. **RES-01**.
2. IF o Redis contiver JSON ou envelope de cache inválido THEN o cache SHALL tratá-lo como miss, sem 500 causado por esse conteúdo. **RES-02**.
3. WHEN uma chamada externa falhar THEN a API SHALL aplicar a tabela normativa de erros e retries abaixo, preservando o envelope sanitizado. **RES-03**.
4. IF a renovação do lock perder propriedade THEN o serviço SHALL cancelar a consulta associada e encerrar em 503 `WEATHER_PROVIDER_UNAVAILABLE`, sem publicar o resultado obtido sem propriedade. **RES-04**.

**Independent Test:** Relógio controlado cruzando TTL, Redis real com chave
inválida e mocks de falha/renovação, sem depender da internet.

### P1: Executar somente com configuração válida

**User Story:** Como operador, quero detectar configuração incorreta antes
de receber tráfego.

**Acceptance Criteria:**

1. IF limites, janelas ou timeouts forem zero/negativos, não finitos, ou retries negativos THEN a inicialização SHALL falhar com erro de configuração sanitizado; retries acima de dois continuarão limitados a dois. **CFG-01**.
2. IF ambiente de produção usar destino meteorológico fora dos hosts HTTPS permitidos, com credenciais na URL ou fragmento THEN a inicialização SHALL rejeitar a configuração. **CFG-02**.

**Independent Test:** Instanciar Settings com valores de fronteira, URLs
indevidas e a exceção explícita do provider-mock em ambiente `load`.

### P1: Controlar acesso de rede e exposição de informações

**User Story:** Como operador, quero limitar consumo e circulação de dados
sem adicionar contas pessoais nesta etapa.

**Acceptance Criteria:**

1. WHEN um cliente chamar a API por proxy THEN a aplicação SHALL aceitar `X-Forwarded-For` somente de peers confiáveis e manter o 429 local com `Retry-After` quando a cota individual se esgotar. **SEC-01**.
2. WHEN uma consulta terminar THEN logs da aplicação e da entrada de homologação SHALL omitir query, IP bruto, tokens e payload meteorológico, mantendo request ID, rota normalizada, status e duração. **SEC-02**.
3. WHEN a imagem de produção for construída THEN ela SHALL executar com UID diferente de zero e sem testes, ferramentas dev ou `.env` em suas camadas finais. **SEC-03**.
4. IF a cota global configurada de chamadas externas estiver esgotada THEN o serviço SHALL impedir uma nova chamada ao provedor e usar somente fallback ainda válido ou retornar 503 `WEATHER_PROVIDER_UNAVAILABLE`. **SEC-04**.

**Independent Test:** Testes de IP forjado, auditoria dos logs com marcadores
de entrada, inspeção da imagem e concorrência em Redis com cota conhecida.

### P2: Homologar operação e observar problemas

**User Story:** Como operador, quero inspecionar saúde e métricas sem expor
interfaces operacionais ao consumidor.

**Acceptance Criteria:**

1. WHEN requisições atingirem rotas inexistentes diferentes THEN as métricas SHALL agrupá-las sob um único rótulo `unmatched`, sem incluir o caminho arbitrário. **OBS-01**.
2. WHEN um operador acessar `/internal/metrics` pela rede interna de homologação THEN a API SHALL retornar snapshot JSON identificado por processo; pela entrada de usuário, a mesma rota responderá 404. **OBS-02**.
3. WHEN a stack de homologação for iniciada THEN a entrada SHALL usar TLS, Redis exigirá credencial e não publicará porta no host, e serviços de carga não terão rota na entrada do usuário. **OPS-01**.
4. WHEN o artefato de dependências de produção for usado em dois builds limpos THEN a instalação SHALL selecionar as mesmas versões registradas, mantendo dependências dev fora da imagem final. **OPS-02**.

**Independent Test:** Smoke local da entrada TLS, conexão Redis permitida e
negada, rota interna e inspeção comparada de duas imagens.

### P2: Consultar o clima pela interface

**User Story:** Como visitante, quero informar um local e período e receber
um resultado compreensível no computador ou no celular.

**Acceptance Criteria:**

1. WHEN o visitante informar texto ou coordenadas e um período válido THEN a interface SHALL enviar somente os parâmetros contratados para `/api/v1/risk`, com escolha Celsius/Fahrenheit. **UI-01**.
2. WHEN a API responder 200 THEN a interface SHALL mostrar local/fuso, período, dias, unidades, risco calculado, completude, fonte, coleta, stale e aviso; alertas terão estado separado. **UI-02**.
3. WHEN houver loading, erro HTTP ou de rede THEN a interface SHALL apresentar o estado e a recuperação descritos no design, respeitando `Retry-After` e ignorando respostas de consultas substituídas. **UI-03**.
4. WHEN a interface for usada por teclado ou em viewport de 360 px THEN ela SHALL manter campos com rótulos, foco visível, mensagens anunciáveis e ausência de rolagem horizontal da página. **UI-04**.

**Independent Test:** Roteiro de navegador com fixture controlada e API local;
inspecionar requisições, estados, foco e layout nos tamanhos especificados.

## Regras normativas de qualidade

Entradas da política por dia: mínima e máxima de temperatura, precipitação
diária, máxima horária de precipitação e rajada máxima.

| Completude    | Condição                                                                                                         |
| ------------- | ---------------------------------------------------------------------------------------------------------------- |
| `complete`    | Todas as entradas da política presentes em todos os dias e série de precipitação com cobertura horária completa. |
| `unavailable` | Nenhuma entrada da política utilizável em todo o período.                                                        |
| `partial`     | Qualquer situação intermediária, inclusive lacuna horária.                                                       |

Cobertura esperada é calculada pelo dia civil no fuso da previsão: 23, 24 ou
25 horas conforme a transição de fuso. Não exigir sempre 24 amostras.
Horários fora de ordem, fora do período ou multiplicidade além da esperada
são dados inválidos (502); amostras ausentes tornam a cobertura parcial.
Horários locais repetidos legitimamente na transição de fuso são aceitos.

`missing_fields` preserva marcadores existentes e acrescenta caminhos
determinísticos como `days.2026-09-13.wind_gust_max_kmh` e
`hourly.2026-09-13.precipitation.coverage`. Nulos não viram zero.
O enum de risco e a política `reference-v1` são preservados. O nível continua
calculado com os dados utilizáveis; a interface nunca o apresenta sozinho
quando a completude for parcial ou indisponível.

## Regras normativas de erros

| Origem / condição              | HTTP / código público                | Retry do backend     | Stale permitido                    |
| ------------------------------ | ------------------------------------ | -------------------- | ---------------------------------- |
| Entrada inválida               | 422 / códigos atuais de entrada      | Não                  | Não                                |
| Local não encontrado           | 404 / `LOCATION_NOT_FOUND`           | Não                  | Não                                |
| Limite por cliente             | 429 / `RATE_LIMIT_EXCEEDED`          | Não                  | Não                                |
| HTTP 429 do provedor           | 503 / `WEATHER_PROVIDER_UNAVAILABLE` | Não nesta rodada     | Sim, para forecast e dentro do TTL |
| Outros 4xx do provedor         | 502 / `WEATHER_PROVIDER_REJECTED`    | Não                  | Não                                |
| Timeout/rede/5xx externo       | 503 / `WEATHER_PROVIDER_UNAVAILABLE` | Até dois adicionais  | Sim, para forecast e dentro do TTL |
| Payload meteorológico inválido | 502 / `WEATHER_DATA_INVALID`         | Não                  | Não                                |
| Redis inacessível              | 503 / `DEPENDENCY_UNAVAILABLE`       | Sem bypass do limite | Não                                |
| Perda de lock                  | 503 / `WEATHER_PROVIDER_UNAVAILABLE` | Não nessa operação   | Não nessa operação                 |
| Exceção inesperada             | 500 / `INTERNAL_ERROR`               | Não                  | Não                                |

As mensagens são fixas, sem texto bruto do upstream; request ID é preservado.
Mudanças de códigos de falhas do provedor são correções deliberadas do 500
atual e precisam de testes de contrato e nota de atualização.

## Edge Cases

- Cache fresco com 599 s; stale com 600 s; expirado em 900 s exatos.
- Stale válido na primeira leitura, expirado após espera por lock ou retry.
- Cache inválido, Redis indisponível e perda de lock durante chamada lenta.
- Dia com 23/25 horas; consultas por coordenadas com fuso diferente de UTC.
- Campos nulos, percentuais 0/100, NaN/infinito e entrada mínima maior que máxima.
- Dois pontos que arredondariam para a mesma chave antiga; nomes distintos para o mesmo ponto.
- Todos os dados de risco ausentes; dado forte de risco presente com outras lacunas.
- 429 do cliente e 429 do provedor com consequências diferentes.
- Resposta antiga chegando depois da consulta mais recente no frontend.

## Requirement Traceability

| Requirement ID | Story                        | Tasks    | Status   |
| -------------- | ---------------------------- | -------- | -------- |
| DAT-01         | Previsão coerente            | T1       | Verified |
| DAT-02         | Previsão coerente            | T2       | Verified |
| DAT-03         | Qualidade explícita          | T3       | Verified |
| DAT-04         | Média de temperatura         | T4       | Verified |
| CON-01         | Identidade do cache          | T5       | Verified |
| RES-01         | Expiração no fallback        | T6       | Verified |
| RES-02         | Cache corrompido             | T7       | Verified |
| RES-03         | Falhas externas              | T8       | Verified |
| RES-04         | Perda de lock                | T9       | Verified |
| CFG-01         | Configuração numérica        | T10      | Verified |
| CFG-02         | Destinos de rede             | T11      | Verified |
| SEC-01         | Limite e proxy               | T12      | Verified |
| SEC-02         | Logs sanitizados             | T13, T20 | Verified |
| SEC-03         | Imagem de produção           | T18      | Verified |
| SEC-04         | Cota externa                 | T14      | Verified |
| OBS-01         | Cardinalidade                | T15      | Verified |
| OBS-02         | Métricas internas            | T16, T20 | Verified |
| OPS-01         | Homologação protegida        | T19, T20 | Verified |
| OPS-02         | Dependências reproduzíveis   | T17, T18 | Verified |
| UI-01          | Consulta                     | T21, T22 | In Tasks |
| UI-02          | Resultado                    | T23      | In Tasks |
| UI-03          | Estados                      | T24      | In Tasks |
| UI-04          | Acesso por teclado e celular | T25      | In Tasks |

**Cobertura planejada:** 23 requisitos, todos mapeados a tarefas; 19
requisitos verificados nos gates T1–T20; revisão independente final pendente.

## Success Criteria

- [ ] Todos os critérios e casos de fronteira têm evidência de verificação.
- [ ] A suíte existente continua passando, sem exclusão de testes para ocultar falhas.
- [ ] Os testes de integração usam Redis real e provedor controlado.
- [ ] A interface passa pelo roteiro local em 360 px e 1280 px.
- [ ] Qualidade, risco heurístico e alertas oficiais têm apresentação distinta.
- [ ] Nenhum teste de carga é apresentado como capacidade do Open-Meteo público.

Passar os validadores destes documentos comprova estrutura e rastreabilidade,
não implementação ou segurança de uma implantação.
