# Arquivo histórico — ImplementationsAndRefactoring

> **Revisão contextual — 30/10/2026.** [Estado vigente](STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Este arquivo preserva registros de lotes anteriores, inclusive resultados e pendências superadas. **Não é o estado atual da aplicação.** Consulte [ImplementationsAndRefactoring](ImplementationsAndRefactoring.md) e [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md). Os caminhos relativos históricos foram mantidos.

## Histórico anterior — não usar como status vigente

## Incrementos de 19/10/2026

Continuações: reconciliação numérica da chuva de Belém por encerramento às 12 UTC;
contagem de suporte observacional; baseline diagnóstica completada para cinco
eventos, incluindo máximos horários civis, com 15 agregações e 180 estratos.
Os dados, limiares e resultados pais foram preservados. Aceite científico pendente.

Auditoria reproduzível de totais mensais; comparações observacionais de 2024 em
três estações; bootstrap pareado por datas; idioma reativo da mensagem de sucesso;
erro/repetição na busca com proteção a falhas atrasadas; frescor/expiração do cache
de alertas; lint, Vitest e auditoria Node configurados na CI. Homologação local
de TLS/Redis/rotação executada parcialmente, com navegador ainda pendente.
Consulte [execução técnica](../planejamento/reference-candidate-1/execucao-2026-10-19.md)
e [validação operacional](../operacoes/validacao-local-2026-10-19.md).

O catálogo abaixo preserva o estado histórico do ciclo anterior.

**Status:** P0–P2.6 concluídos; revisão independente final pendente.  
**Última atualização:** 25 de setembro de 2026.
**Projeto:** ClimaPrev

## Objetivo

Este documento registra as alterações implementadas no ciclo atual, as
decisões tomadas e o trabalho que permanece no planejamento. Ele serve como
handoff para retomar o projeto sem depender do histórico da conversa.

O termo correto em inglês para melhoria estrutural de código é
**refactoring**.

## Estado atual

As tarefas autorizadas até **P2.6** foram concluídas. O código atual contém:

- frontend estático separado do pacote Python;
- backend FastAPI orientado a API;
- entrega local pelo Nginx;
- controles de segurança, proxy e limites operacionais;
- cache e coordenação Redis com resiliência;
- integração de alertas oficiais do INMET em seção separada;
- busca de localidades com sugestões;
- cancelamento, timeout e mensagens acessíveis no frontend;
- documentação dos parâmetros usados na predição.

### Rework do frontend com Vue — 23 de setembro de 2026

- Substituiu a manipulação direta do DOM por Vue 3 e Composition API.
- Adicionou TypeScript `strict`, Vite, Vitest e ESLint.
- Tipou a consulta, a resposta de risco, erros, qualidade dos dados e alertas.
- Separou formulário, autocomplete, consulta, risco, previsão diária e alertas
  em componentes e composables.
- Preservou POST same-origin, timeout, cancelamento, rate limit, foco, teclado,
  live region e ausência de persistência da localização.
- Criou build multi-stage Node → Nginx, com assets hashados e sem `node_modules`
  na imagem final.
- Atualizou local e homologação para usar a mesma imagem compilada e manteve
  suas configurações de proxy independentes.
- Atualizou os gates estáticos, de segurança, contrato POST e assets dinâmicos.
- Corrigiu o smoke test da CI para descobrir os assets hashados diretamente do
  HTML, sem depender do antigo `/assets/styles.css`.

## Alterações implementadas

### P0 — Separação do frontend e do backend

- Moveu os arquivos estáticos de `src/climaprev/web/` para `frontend/`.
- Removeu o serviço de HTML e assets do FastAPI.
- Removeu o `package-data` que incluía arquivos web no pacote Python.
- Ajustou os testes para validar a nova fronteira entre API e frontend.
- Criou `docker/frontend/nginx.conf`.
- Adicionou o serviço `frontend` ao Compose local.
- Manteve a interface em `http://127.0.0.1:8080` e a API direta em
  `http://127.0.0.1:8000` para diagnóstico.
- Corrigiu a entrega dos assets pelo Nginx, incluindo MIME types e o alias de
  `/assets/`.

### P1.1–P1.2 — Superfície pública e documentação da API

- Adicionou headers de segurança no Nginx: `nosniff`, `Referrer-Policy`,
  `Permissions-Policy`, `X-Frame-Options` e `Content-Security-Policy`.
- Restringiu Swagger, ReDoc e OpenAPI ao ambiente de desenvolvimento.
- Manteve métricas internas fora da superfície pública.
- Adicionou testes de fronteira para rotas públicas, internas e desconhecidas.

### P1.3 — Proxy confiável e identidade do cliente

- Configurou a confiança explícita no proxy conhecido.
- Ajustou a leitura de `X-Forwarded-For` e `X-Real-IP`.
- Configurou o Nginx para encaminhar os headers de forma consistente.
- Preservou o rate limit contra headers forjados por clientes não confiáveis.

### P1.4 — Consulta por POST

- Adicionou `POST /api/v1/risk` com corpo JSON validado pelo mesmo contrato do
  endpoint GET.
- Atualizou o frontend para enviar os dados da consulta no corpo da requisição.
- Manteve o GET para compatibilidade e diagnóstico.
- Reduziu a exposição de localização em URLs, históricos e logs de acesso.

### P1.5 — Endurecimento dos containers

- Fixou as imagens por versões explícitas.
- Aplicou filesystem somente leitura onde compatível.
- Removeu capabilities desnecessárias e ativou `no-new-privileges`.
- Restringiu portas e redes conforme o papel de cada serviço.
- Preservou health checks e o funcionamento do alvo de desenvolvimento.

### P1.6 — Lock Redis com backoff

- Substituiu polling agressivo por backoff exponencial limitado.
- Adicionou jitter para reduzir sincronização entre concorrentes.
- Definiu limite de tentativas e deadline de espera.
- Registrou contenção e timeout do lock nas métricas.

### P1.7 — Observabilidade

- Adicionou métricas de latência e resultado por provedor.
- Registrou cache hit, stale e miss.
- Registrou retries, erros upstream, contenção e timeout de lock.
- Manteve os registros sanitizados e a rota de métricas interna.

### P1.8–P1.9 — Performance do provedor e dos assets

- Removeu campos horários não utilizados pelo domínio.
- Manteve as séries meteorológicas necessárias para a resposta e o cálculo.
- Configurou cache controlado para CSS e JavaScript.
- Configurou revalidação frequente para o HTML.
- Adicionou verificações estáticas para MIME types, headers e cache.

### P1.10–P1.11 — Alertas opcionais e cliente HTTP compartilhado

- Criou a porta de alertas oficiais sem misturá-la ao risco heurístico.
- Compartilhou o `httpx.AsyncClient` entre adaptadores.
- Configurou limites de conexões, keep-alive e timeouts explícitos.
- Limitou retries a falhas transitórias e evitou retry indiscriminado de 429.
- Preservou a proteção contra destinos externos não permitidos.

### P2.1 — Alertas oficiais do INMET

- Adicionou o adaptador `InmetOfficialAlertsProvider`.
- Consultou o endpoint oficial de avisos ativos do INMET.
- Interpretou alertas de hoje e futuros.
- Validou polígonos GeoJSON e a localização consultada.
- Filtrou alertas pelo período solicitado e pelo fuso local.
- Exibiu origem, evento, severidade, vigência, área e URL de origem.
- Separou os estados `available` e `unavailable` do cálculo de
  `forecast_risk`.
- Adicionou cache de sucesso e cache curto de indisponibilidade.

### P2.2 — Política de risco

- Revisou a política `reference-v1` e seus limiares.
- Não alterou os limiares por falta de dados históricos rotulados e avaliação
  especializada.
- Registrou que a política atual é heurística e orientativa.
- Manteve a necessidade futura de calibração científica por região e estação.

### P2.3 — Busca de localidades

- Adicionou `GET /api/v1/locations/search`.
- Limitou a consulta a texto entre 2 e 100 caracteres.
- Aplicou rate limit à busca.
- Retornou até cinco candidatos com nome, coordenadas, fuso e fonte.
- Adicionou sugestões no frontend com seleção por teclado e mouse.
- Encaminhou a nova rota pelo Nginx local.
- Manteve a confirmação da localidade antes do envio da previsão.

### P2.4 — Horizonte da previsão

- Manteve o contrato de até sete dias inclusivos.
- Não inventou um horizonte fixo adicional sem contrato do provedor.
- Preservou a validação de datas no schema, frontend e testes.

### P2.5 — Estados de consulta

- Adicionou timeout de dez segundos no navegador.
- Adicionou botão de cancelamento.
- Aborta requisições substituídas ou canceladas.
- Impede que uma resposta antiga sobrescreva uma consulta mais recente.
- Adicionou mensagens específicas para timeout, cancelamento e erro.
- Aplicou `role="alert"` às mensagens de erro.

### P2.6 — Acessibilidade e usabilidade

- Preservou HTML semântico, labels e navegação por teclado.
- Adicionou foco visível, skip link e região de status anunciável.
- Melhorou o tamanho e o estado dos controles interativos.
- Validou sugestões de localidade, foco e seleção no navegador.
- Verificou o layout em viewport desktop e móvel.
- Conferiu headers, MIME types e cache dos assets.

## Documentação criada ou atualizada

- `docs/frontend/Frontend-Rework.md`: separação entre frontend e backend.
- `docs/projeto/PossivelPlanoDeEvolução.md`: plano amplo de evolução.
- `Visualização geral do projeto.md`: visão geral técnica na raiz do projeto.
- `docs/arquitetura/parametros-de-predicao.md`: parâmetros de entrada,
  variáveis meteorológicas e limiares do risco.
- `docs/projeto/PROJECT.md`: índice e mapa da documentação.
- Este arquivo: catálogo consolidado de implementações e refatorações.

## Validações realizadas

- Backend: **195 testes unitários/contratuais aprovados** nesta auditoria; a
  suíte de integração completa depende dos serviços Redis/Compose.
- Ruff aprovado; a verificação foi executada ignorando `EXE002`, que é ruído
  de permissões/shebang preexistente nos arquivos do repositório.
- Mypy aprovado em 41 arquivos de origem.
- Configuração do Docker Compose aprovada.
- `nginx -t` aprovado dentro do container frontend.
- Smoke tests do proxy local aprovados.
- CSS retorna `text/css` e JavaScript retorna `application/javascript`.
- Cache e headers de segurança dos assets verificados.
- Busca de localidades validada pela API e pelo navegador.
- Foco e seleção de sugestão verificados no navegador.

### CI — Validação automática

- Criou `.github/workflows/ci.yml`, acionado por `push`, Pull Request e
  execução manual.
- Reutilizou o Docker Compose para build, suíte completa, Ruff, mypy e
  validação da configuração do Nginx.
- Adicionou smoke test HTTP para a página, assets hashados e health check da
  API por meio de `tests/docker/check_frontend_security.py`.
- Limitou as permissões do workflow a leitura do conteúdo do repositório e
  encerrou os serviços temporários ao final da execução.

Não foi executada uma certificação formal com Lighthouse ou leitor de tela.
As verificações de acessibilidade desta etapa foram smoke tests funcionais,
DOM, foco, teclado, viewport e headers.

## Itens ainda pendentes

### Estado operacional da cópia correta

- A pasta `climaprev-Atualizacao-Geral-V3` está conectada ao repositório Git
  correto na branch `Atualizacao-Geral-V3`, acompanhando
  `origin/Atualizacao-Geral-V3`.
- As alterações atuais ainda não foram commitadas nem enviadas. O próximo
  passo é revisar o staging e criar o commit da atualização.
- Os arquivos `.homolog/` não são versionados; devem ser provisionados
  localmente com secrets e certificados antes de iniciar a homologação.
- As dependências do frontend foram atualizadas para corrigir as vulnerabilidades
  encontradas no Vitest/Vite. O `npm audit` atual retorna zero vulnerabilidades;
  a instalação continua registrada no `package-lock.json`.

### Próximo item técnico

- Executar a revisão independente final com evidência por requisito e testes
  em uma cópia isolada.

### Evolução do produto

- Calibrar cientificamente a política de risco com dados históricos e revisão
  especializada.
- Executar o piloto offline de validação descrito em [possível continuação e
  viabilidade de aumento de escopo](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md).
- Completar o contrato operacional de alertas oficiais, incluindo cobertura,
  expiração, monitoramento e critérios de disponibilidade.
- Definir contas, autorização, favoritos, histórico e retenção de dados.
- Definir notificações, consentimento, cancelamento e idempotência.
- Preparar implantação pública com domínio, TLS real, secrets, cotas,
  observabilidade e rollback.
- Configurar checks obrigatórios da CI na branch principal após confirmar a
  primeira execução no GitHub.
- Criar ADRs para as decisões arquiteturais principais.

## Como retomar

1. Ler este documento, `STATE.md` e `ROADMAP.md`.
2. Conferir o estado real do working tree antes de editar arquivos.
3. Começar pela revisão independente final.
4. Para qualquer nova alteração de código, descrever processo, ganho,
   impacto e validação antes da execução.
5. Executar testes direcionados e depois a suíte relevante.
6. Atualizar este catálogo quando uma nova etapa for concluída.

## Documentos relacionados

- [Visão geral do projeto](PROJECT.md)
- [Arquitetura](../arquitetura/arquitetura.md)
- [Parâmetros de predição](../arquitetura/parametros-de-predicao.md)
- [Possível continuação e escopo de previsão](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md)
- [Operações](../operacoes/operations.md)
- [Plano de evolução](PossivelPlanoDeEvolu%C3%A7%C3%A3o.md)
- [Reestruturação do frontend](../frontend/Frontend-Rework.md)

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
