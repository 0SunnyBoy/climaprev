# Arquivo histórico — STATE

> **Revisão contextual — 30/10/2026.** [Estado vigente](STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Este arquivo preserva registros de lotes anteriores, inclusive resultados e pendências superadas. **Não é o estado atual da aplicação.** Consulte [STATE](STATE.md) e [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md). Os caminhos relativos históricos foram mantidos.

## Registros históricos preservados

As seções datadas abaixo descrevem seus respectivos lotes. Contagens menores, gates pendentes e prioridades anteriores não substituem o estado vigente acima.

## Estado atual — 2026-10-19

Checkout Git `climaprev-develop`, branch `develop`, base 23bf4ce e alterações
locais sem commit/push. Os registros datados abaixo são históricos; as antigas
afirmações de cópia sem Git ou ausência de `.homolog/` não descrevem esta pasta.

- Reference-v1 ativa, calibração desativada; nenhuma candidata promovida.
- CSVs oficiais de 2024 para A201/A001/A801 obtidos e comparados nos 36 snapshots
  preservados; 72 relatórios e síntese pareada gerados. Aceite científico pendente.
- Reconciliação numérica de chuva de Belém concluída: o dia encerrado às 12 UTC,
  com fronteira de dezembro, reproduz 417,0 mm, 384,4 mm até 30/01 e 56,2 mm em 09/01.
  Adequação científica permanece pendente; dados e limiares preservados.
- Suporte observacional alto de 2024: 2 dias de chuva horária, 4 de chuva diária,
  3 de rajada, nenhum de calor/frio; contagens por evento não são independentes.
- Bootstrap por blocos implementado e testado, sem inferência científica aprovada.
- Baseline diagnóstica dos cinco eventos calculada, com 15 agregações e 180 estratos.
  Nenhum dos quatro altos de chuva diária ou três de rajada foi detectado pelo GFS
  nos três horizontes do recorte; não é uma medida geral de desempenho da API.
  Chuva horária foi pareada em 36 relatórios, sem detecção dos dois altos pelo GFS
  nos três horizontes. Aceites científicos permanecem pendentes. Detalhes em
  [chuva horária e baseline atual](../planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md).
- 574 testes backend aprovados no lote de chuva horária; 10 frontend aprovados
  no lote anterior, sem mudanças posteriores na interface. Build/typecheck, ESLint, Ruff e
  mypy aprovados. A configuração de CI inclui lint/Vitest/auditoria Node, ainda local.
- Corrigidos idioma da mensagem de sucesso, recuperação da busca e frescor do
  cache de alertas. Geometrias, cobertura e validade integral dos avisos continuam pendentes.
- Homologação TLS isolada provisionada; topologia, hardening, proxy, CA, logs,
  Redis e rotação sintética verificados. Runner de navegador não foi obtido após
  duas transferências interrompidas; gate não executado. Não há aceite público.

Detalhes: [execução técnica](../planejamento/reference-candidate-1/execucao-2026-10-19.md),
[validação operacional](../operacoes/validacao-local-2026-10-19.md) e
[RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-19.md).

## Auditoria da cópia de desenvolvimento — 2026-09-25

A cópia `climaprev-develop-build` contém o código, frontend Vue, Docker, testes
e documentação sincronizados. Ela é um build sem metadados `.git`, portanto não
é um checkout adequado para commit ou push. Nesta auditoria:

- build do backend e do frontend aprovado;
- Compose local e de homologação aprovado em modo `config`;
- Ruff e mypy aprovados;
- 463 testes backend aprovados;
- 5 testes frontend aprovados;
- lint, typecheck, Vitest e build Vite aprovados;
- smoke test do Nginx, assets hashados e headers aprovado;
- dependências de produção do frontend sem vulnerabilidades conhecidas no lock.
- dependências do frontend atualizadas para Vitest 5.0.2 e Vite 6.4.3; `npm
  audit` retornou zero vulnerabilidades.
- pipeline offline de validação histórica executado contra as APIs da Open-Meteo,
  sem banco de dados e sem ativar calibração;
- amostra real de três dias em Belém, com antecedência de um dia: 3 casos
  comparáveis, 3 classificações corretas e nenhum falso positivo ou negativo.

O workflow da CI foi corrigido para descobrir CSS e JavaScript pelo HTML do
Vite. A validação atual confirmou Redis saudável,
frontend HTTP 200, health check HTTP 200, assets e contratos do frontend.
As alterações desta etapa ainda não foram commitadas nem enviadas ao GitHub,
pois a cópia não possui `.git`. Elas devem ser aplicadas em um checkout da
branch `develop` antes da publicação.

A homologação real ainda depende do provisionamento local de `.homolog/`, que
não existe nesta cópia e não deve ser versionado.

## Estado de publicação — 2026-09-25

- Branch de desenvolvimento esperada: `develop`.
- A pasta atual não é um checkout Git.
- Próximo passo Git: clonar ou usar um checkout limpo de `develop`, reaplicar
  as alterações, revisar o diff, criar o commit e executar o push.
- Nenhum commit, push, merge ou deploy foi executado nesta etapa.

## Segurança — atualização de 2026-09-23

A implementação de segurança em `Atualizacao-Geral-V3` continua **sem
prontidão de produção**. T14 passou na stack sintética de homologação com
TLS/ACL, logs e isolamento; T15 passou no runner Playwright pinado em HTTP
e HTTPS com CA explícita; T16 passou no Gitleaks com regras padrão e teste
de segredo sintético. T17 passou também no workflow de segurança do GitHub
para `525854a`. T18 tem runbook e ensaio de
rotação sintética; T19 consolidou decisão condicional. A revisão independente
do proprietário e a validação do ambiente real continuam pendentes.
Leia o [contexto atual](../planejamento/seguranca-configuracao-segredos/context.md)
e as [evidências](../planejamento/seguranca-configuracao-segredos/evidence.md).

Os resultados abaixo são históricos, anteriores a esse ciclo, e não aprovam
o código novo. Alterações locais anteriores de frontend, Compose e outros
documentos foram preservadas fora do checkpoint de segurança.

## Registro anterior — 2026-09-18

**Atualização:** 18 de setembro de 2026.  
**Estado:** P0–P2.6 concluídos; revisão independente final pendente.

[Índice](PROJECT.md) · [Roadmap](ROADMAP.md) · [Tarefas base](../planejamento/evolucao-climaprev/tasks.md)

## Execução atual

As 25 tarefas do ciclo base foram concluídas. O ciclo recebeu incrementos
adicionais até P2.6, conforme o catálogo
[Implementations and refactoring](ImplementationsAndRefactoring.md).

### Arquitetura e frontend

- O frontend Vue/TypeScript está em `frontend/`, é compilado pelo Vite e servido pelo Nginx local.
- O FastAPI funciona como backend API, health check e superfície interna.
- O Compose local expõe a interface em `127.0.0.1:8080` e a API direta em
  `127.0.0.1:8000`.
- O frontend usa consulta same-origin, busca de localidades e POST para risco.

### Backend, segurança e operação

- A API valida localização, coordenadas, datas, unidade e período de até sete
  dias.
- O proxy confiável preserva a identidade do cliente sem aceitar headers
  forjados de origens não confiáveis.
- Rate limit, orçamento de provedor, timeouts, retries e limites de conexão
  estão configurados.
- O Redis usa cache, lock distribuído com backoff/jitter e métricas de
  contenção.
- O Nginx aplica headers de segurança e mantém rotas internas fora da
  superfície pública.

### Provedores e predição

- Open-Meteo fornece geocodificação e previsão meteorológica.
- O INMET fornece alertas oficiais ativos por local e período.
- A política `reference-v1` continua heurística e orientativa.
- Os alertas oficiais aparecem separados de `forecast_risk` e têm prioridade
  no novo `risk_overview`.
- `forecast_risk.daily` avalia cada dia e `peak_days` destaca todos os dias
  empatados no maior nível do período.
- A validação histórica está disponível como protocolo offline; a calibração
  estatística continua desativada (`disabled`) até haver dados revisados.
- Localidades inválidas são rejeitadas antes da consulta quando coordenadas ou
  o fuso horário IANA não passam pela validação de domínio.
- A chave de cache inclui a versão do perfil de calibração, evitando misturar
  respostas calculadas com perfis diferentes.
- A busca de localidades retorna até cinco sugestões e preserva a confirmação
  da localidade antes da consulta.

### Experiência do usuário

- O formulário permite cidade ou coordenadas.
- O período aceita de um a sete dias.
- A interface oferece Celsius ou Fahrenheit para exibição das temperaturas.
- O usuário pode cancelar uma consulta ou aguardar o timeout de dez segundos.
- Respostas antigas não sobrescrevem consultas mais recentes.
- Mensagens de erro, status, foco e navegação por teclado foram revisados.

## Evidências executadas

- Suíte completa: **341 testes aprovados**.
- Ruff aprovado com `EXE002` ignorado por ser ruído de permissões/shebang
  preexistente no repositório.
- Mypy aprovado em 41 arquivos de origem.
- Configuração do Docker Compose aprovada.
- Build e inicialização da stack local aprovados.
- `nginx -t` aprovado no container frontend.
- Smoke test do proxy local aprovado.
- CSS e JavaScript retornam MIME types corretos e headers de cache esperados.
- Endpoint de busca de localidades retorna candidatos válidos.
- Navegador confirmou sugestões, seleção, foco e ausência de erros de console.
- Workflow de CI criado para repetir build, testes, análise estática, mypy,
  Nginx e smoke test no GitHub; primeira execução remota depende do push.

### Retomada de segurança — 2026-09-21

- Suíte completa após o checkpoint: **437 testes aprovados**.
- Build das imagens `app` e runtime com a base Python 3.12 Alpine fixada por
  digest: aprovados.
- Ruff com `--ignore EXE002`: aprovado; mypy em 41 arquivos: aprovado.
- Nginx local: `nginx -t` aprovado; body acima de 16 KiB retornou 413,
  método PUT indevido 403 e rota desconhecida 404.
- Frontend/assets e contrato de segurança estático/HTTP: aprovado.
- Perfil de carga: Redis e redes próprios, ambos `internal: true`; smoke
  Locust de 3 requisições, 0 falhas.
- Ensaio sintético de rotação: aprovado, conjuntos independentes e sem
  valores exibidos.
- Gitleaks 8.30.1 passou com regras padrão, exceção por fingerprint para
  um falso positivo histórico e fixture que detecta token sintético; 33
  commits examinados. Trivy 0.74.0 passou com 0 HIGH/CRITICAL na imagem
  runtime Alpine; `ignore-unfixed` permanece desativado.
- Validação manual adicional no navegador local: página, assets, validação
  nativa, consulta sintética, renderização do resultado e console sem erros.
- Runner Playwright `1.63.0` executado em container de teste pinado:
  fluxo local HTTP e homologação HTTPS passaram, sem ignorar erros TLS.

As verificações de acessibilidade foram funcionais e visuais. Não houve
certificação formal por Lighthouse ou leitor de tela nesta etapa.

## Pendências

- Executar revisão independente em uma cópia isolada, com evidência por
  requisito.
- Calibrar a política de risco com dados históricos e avaliação especializada;
  a camada técnica já existe, mas permanece desativada até esse conjunto de
  evidências ser aprovado.
- Ampliar o piloto offline de validação descrito no [plano de continuação e
  viabilidade de escopo](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md),
  cobrindo diferentes regiões, estações, horizontes de 1 a 7 dias e revisão
  especializada. A ferramenta técnica já está disponível; falta avaliar uma
  amostra suficiente para qualquer decisão científica ou de calibração.
- Consolidar cobertura, expiração, monitoramento e operação dos alertas oficiais.
- Definir contratos de identidade antes de contas, favoritos, histórico ou
  notificações.
- Planejar implantação pública, secrets, cotas, observabilidade, CD e rollback.

## Decisões preservadas

- A interface normal é o frontend em `:8080`.
- A porta `:8000` é API direta e diagnóstico.
- A consulta continua anônima e não armazena localização no navegador.
- O risco é uma estimativa baseada em previsão, não um alerta oficial.
- Alertas oficiais não alteram diretamente o nível heurístico.
- Dados ausentes permanecem sinalizados; não são transformados em zero.
- O horizonte máximo permanece em sete dias inclusivos.

## Retomada

Os próximos gates são, nesta ordem: homologação TLS/ACL (T14), runner
Playwright reproduzível e CI remoto (T15/T17), revisão do runbook de rotação
(T18) e revisão independente final (T19). Qualquer nova alteração de código
deve registrar processo, ganho esperado, impacto e validação antes da execução.

### Incremento espacial — 19/10/2026

Plano espacial congelado em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md e evidence/plano-espacial-2024-2026-10-19.json: 72 snapshots previstos, com controle municipal novo e braço nas coordenadas INMET de 2024, altitude e seleção de célula fixas por par. Sete testes novos aprovados, mypy aprovado. Coletor, preflight do provedor, coleta e comparação ainda pendentes; nenhum resultado espacial ou ganho de previsão declarado. Mantidos reference-v1 ativa e bloqueio de fitting/etapa 6.

### Execução espacial concluída — 19/10/2026

O incremento espacial anterior avançou: coletor e pareamento implementados, preflight real aprovado, 72 snapshots coletados sem falhas, 180 estratos e 30 agregações comparados, sem perda adicional dos dias elegíveis anteriores. Os resultados são mistos; nenhuma detecção dos altos de chuva horária/diária/rajada foi recuperada e a temperatura mínima teve MAE maior nos três horizontes. Reference-v1 mantida, sem fitting ou promoção. Próximo incremento: catálogo dos casos altos perdidos e falsos alarmes, seguido de consolidação dos limites e critérios científicos. Detalhes e evidências em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md. As pendências de coletor/coleta citadas no registro anterior estão concluídas.

### Catálogo e diagnóstico — 19/10/2026

Catálogo espacial concluído com 3.747 casos e reconciliação dos 180 estratos; valores, classes moderada/alta, margens aos limiares, ambos os braços/fontes e hashes preservados. Altos observados concentrados em seis unidades local/data; não recuperados por GFS ou ERA5. Consulta na estação melhora detecção de calor moderado, mas aumenta falsos alarmes. 85 testes direcionados aprovados, Ruff e mypy do módulo novo aprovados. Dois subagentes fizeram revisões independentes read-only de integridade/resultados e pendências científicas. Diagnóstico/adendo em docs/planejamento/reference-candidate-1/diagnostico-e-adendo-2026-10-19.md. Próximos: diagnóstico horário nos dados existentes, auditoria de reservas e decisões científicas; fitting/etapa 6 continuam bloqueados.

### Diagnóstico horário e inventário local — 19/10/2026

Concluídos diagnóstico de 37 registros relevantes para alto, com perfis e recompostos conferidos, e inventário local de reservas: 114 snapshots conhecidos, 14 artefatos de testes, zero origem desconhecida e zero correspondência conhecida com períodos reservados. Isso não certifica independência das reservas nem ausência de acesso externo/anterior. 88 testes direcionados aprovados; Ruff e mypy do módulo temporal aprovados. Versões iniciais preservadas; evidências atuais com sufixo v2. Detalhes em docs/planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md. Próximos: revisão científica e proveniência, critérios de aceite e protocolo prospectivo final; etapa 6 bloqueada. Nenhuma alteração no PDF acadêmico.

### Desacoplamento de implantação — 20/10/2026

Frontend com contexto Docker/Nginx/Compose/documentação próprios; API origin configurável no build, CSP restrita e sem proxy app no modo externo. API com Compose próprio e CORS JSON/headers expostos configurados. Modo integrado preservado; CI/homologação atualizadas. Verificações: 18 testes frontend e 37 API/segurança, build/typecheck/lint/Ruff/mypy, Composes e Nginx sem rede com HTTP 200 aprovados. Navegador end-to-end/domínios reais permanecem pendentes. Detalhes em docs/arquitetura/desacoplamento-2026-10-20.md e RELATORIO-PENDENCIAS-2026-10-20.md. Monorepo preservado; nenhuma publicação ou alteração científica.

### Desacoplamento validado em navegador — 20/10/2026

Concluído o escopo técnico local de separação: gate HTTPS no Edge com frontend/API em origens distintas, busca/POST/resultado via API real, 503, 429 com headers e cooldown, origem bloqueada e interface disponível com processo da API parado. Apenas upstream meteorológico sintético. TLS: cadeia/hostname verificados com CA explícita; navegador com pin SPKI restrito ao processo, sem trust global. Evidência em docs/operacoes/evidence/desacoplamento-browser-2026-10-20.json; reprodução em tests/docker/decoupling/README.md. Modo integrado regressivo aprovado nos gates estático/HTTP/proxy. Job de CI configurado, execução remota e produção não afirmadas. Bancada isolada encerrada. Sem separação de repositórios, publicação ou alteração científica.

### Datas/fusos atuais e horizonte futuro — 20/10/2026

Correção técnica da janela atual concluída: sete datas inclusivas de hoje UTC até +6, API GET/POST rejeita fora da janela antes do serviço e UI informa/atualiza limites na virada de dia e retorno ao foco. Dias meteorológicos mantêm fuso local. 618 testes backend e 20 frontend aprovados, build/typecheck/lint/Ruff/mypy, gate HTTPS com calendário/422 e smoke integrado aprovados. Fixtures isoladas de hosts do Compose e relógios DST, sem remover proteções reais. Ampliação para 14 datas com sete dias por consulta apenas registrada no RDP, não ativada por orientação do usuário. Detalhes em docs/arquitetura/datas-e-fusos-2026-10-20.md. Próximas frentes técnicas: validade/cobertura de alertas e prazo global de consulta; decisões científicas seguem pendentes.


### Encerramento técnico local das frentes — 20/10/2026

Alertas com validade/cobertura conservadoras, prazo cooperativo global de 7 s, interface com contexto/foco/idioma reativos, CI ampliada, exporter privado por worker e carga local implementados. Validação: 644 testes backend e 27 frontend, build/tipagem/lint/actionlint e imagem runtime UID 10001 sem ferramentas de desenvolvimento aprovados. Cinco cenários de carga: 3.000 requisições, zero falhas, cerca de dez req/s, maior p95 580 ms; sem alegação de capacidade de produção. INMET real não confirmado (erro de protocolo), CI remota não executada e monitoramento externo não instalado. Hospedagem/publicação adiadas expressamente pelo usuário; não priorizar infraestrutura. Reference-v1 e janela atual de sete datas preservadas; 14 dias apenas planejado e decisões científicas independentes continuam pendentes. Detalhes e evidências: docs/operacoes/execucao-frentes-1-a-7-2026-10-20.md e RELATORIO-PENDENCIAS-2026-10-20.md. PDF acadêmico preservado.
