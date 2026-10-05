# STATE — Clima Prev

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
