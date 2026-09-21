# STATE — Clima Prev

## Checkpoint de segurança — 2026-09-21

A implementação de segurança em `Atualizacao-Geral-V3` está **pausada e
incompleta**. O usuário solicitou o envio de um checkpoint para continuidade
por outro Codex. Leia o [contexto atual](../planejamento/seguranca-configuracao-segredos/context.md)
e as [evidências](../planejamento/seguranca-configuracao-segredos/evidence.md)
antes de retomar. T1–T9 têm alterações escritas com validação ainda parcial;
T10–T19 permanecem pendentes. A homologação precisa integrar os novos secrets.

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

- O frontend está em `frontend/` e é servido pelo Nginx local.
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
- Os alertas oficiais aparecem separados de `forecast_risk`.
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

As verificações de acessibilidade foram funcionais e visuais. Não houve
certificação formal por Lighthouse ou leitor de tela nesta etapa.

## Pendências

- Executar revisão independente em uma cópia isolada, com evidência por
  requisito.
- Calibrar a política de risco com dados históricos e avaliação especializada.
- Executar o piloto offline de validação descrito no [plano de continuação e
  viabilidade de escopo](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md).
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

O próximo passo do planejamento é a revisão independente final. Qualquer nova
alteração de código deve registrar processo, ganho esperado, impacto e
validação antes da execução.
