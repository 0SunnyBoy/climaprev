# Arquivo histórico — handoff

Este arquivo preserva registros de lotes anteriores, inclusive resultados e pendências superadas. **Não é o estado atual da aplicação.** Consulte [handoff](handoff.md) e [RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md). Os caminhos relativos históricos foram mantidos.

## Histórico anterior — não usar como status vigente

## Retomada vigente — 19/10/2026

Usar o checkout `climaprev-develop`, branch `develop`, base 23bf4ce. Há alterações
experimentais e correções locais sem commit; preservar o diff. A aplicação local
foi atualizada e a stack de homologação foi provisionada separadamente, com
credenciais sintéticas rotacionadas em `.homolog/next/`. Não versionar esse diretório.

Ler [STATE](STATE.md), [RDP](../../RELATORIO-PENDENCIAS-2026-10-19.md) e
[execução científica/técnica](../planejamento/reference-candidate-1/execucao-2026-10-19.md).
Priorizar as pendências científicas, contratos funcionais e gates ainda abertos.
Na continuação, o dia encerrado às 12 UTC e a fronteira de dezembro reconciliaram
os três valores publicados de chuva de Belém. Foram contados os eventos observados
de 2024 e 564 testes backend passaram. Consultar o documento de reconciliação
referenciado na execução técnica antes de reabrir a antiga divergência numérica.
A continuação seguinte calculou a baseline diagnóstica de quatro eventos e um
preflight de suficiência, com 570 testes backend aprovados. Ler a proposta de
critérios antes de congelar alvos; evento/métrica principal e aceite científico
continuam indefinidos. Não usar acurácia agregada para encerrar a avaliação dos altos.
No lote seguinte, os máximos de chuva horária foram pareados em 36 relatórios,
completando cinco eventos, 15 agregações e 180 estratos. Consultar o documento de
chuva horária para as versões atuais; os arquivos de quatro eventos são históricos.
O lote de chuva horária encerrou com 574 testes backend aprovados, Ruff/mypy
aprovados e imagem de desenvolvimento reconstruída. O timeout Redis inicial foi
preservado no registro operacional; não foram removidos testes para obter aprovação.
Reference-v1 ativa, sem ajuste autorizado. O PDF da faculdade não deve receber
novas atualizações; manter os documentos técnicos do projeto atualizados.

As referências à branch V3 e à cópia sem Git abaixo pertencem aos handoffs antigos.

## Estado atual da cópia correta — 2026-09-23

O trabalho atual ocorre em `climaprev-Atualizacao-Geral-V3`, na branch
`Atualizacao-Geral-V3`, conectada a `origin/Atualizacao-Geral-V3`. O rework do
frontend Vue 3 + TypeScript, o build Docker e a validação local integrada foram
concluídos. As alterações ainda não foram commitadas nem enviadas.

O próximo passo é revisar o diff, criar o commit e publicar a branch. A pasta
`.homolog/` permanece local e ausente desta cópia; a homologação real exige
provisionamento separado e não deve receber segredos do Git.

O restante deste documento é um registro histórico do handoff de 2026-08-29.

> Para retomar a segurança da branch `Atualizacao-Geral-V3`, leia primeiro o
> [contexto de 2026-09-21](../planejamento/seguranca-configuracao-segredos/context.md).
> A implementação está pausada e incompleta. O registro abaixo é histórico e
> não representa a validação desse checkpoint.

> Registro histórico de 2026-08-29. Para o estado atual, consulte [STATE](STATE.md),
> [ROADMAP](ROADMAP.md) e [Implementations and refactoring](ImplementationsAndRefactoring.md).

Data: 2026-08-29
Estado: **Task 9 concluída e aprovada; trabalho pausado.**

## Estado técnico

O backend MVP FastAPI está implementado como monólito modular stateless, com:

- `GET /api/v1/risk` por texto ou coordenadas, período de até sete dias;
- seleção de `temperature_unit=celsius|fahrenheit`, com cálculo canônico em
  Celsius;
- adaptadores Open-Meteo protegidos por portas de aplicação;
- política de risco determinística, versionada e explicitamente heurística;
- `official_alerts` separado e `not_configured`;
- Redis para cache, stale fallback, lock distribuído e rate limit;
- request ID, logs estruturados, métricas e health checks;
- perfil Docker de carga com app FastAPI real, Redis real e mock Open-Meteo.

## Evidências

- `docker compose run --rm app pytest -q -W error`: **148 passed**.
- `docker compose run --rm app ruff check src tests`: passou.
- `docker compose run --rm app mypy src`: passou em 32 arquivos.
- Suite de carga: **16 test cases passed**.
- Baseline final: 60.000 requisições em 600 s, 100,14 req/s, p50/p95/p99
  120/160/180 ms, 0 falhas, 0 respostas 5xx e 0 respostas 429.
- Cenários de 30 s: `cold_cache` p95 140 ms, `lock_contention` p95 65 ms,
  `slow_upstream` p95 410 ms e `redis_latency` p95 430 ms; todos sem falhas.
- Revisão independente final: **APPROVED**, sem achados médios ou altos.

Artefatos de evidência:

- `.superpowers/sdd/climaprev-backend-mvp/task-9-baseline-20260829-final.txt`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-scenario-measurements-20260829.txt`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-report.md`
- `.superpowers/sdd/climaprev-backend-mvp/task-9-review.md`

## Documentação de referência

A lista abaixo é somente para leitura e retomada de contexto; não é uma lista
de arquivos para upload. O diretório `.specs/` fica explicitamente fora de
qualquer staging, commit ou push.

Leia, nesta ordem:

1. `.specs/STATE.md`
2. `.specs/features/climaprev-backend-mvp/context.md`
3. `.specs/features/climaprev-backend-mvp/spec.md`
4. `.specs/features/climaprev-backend-mvp/design.md`
5. `.specs/features/climaprev-backend-mvp/tasks.md`
6. `docs/superpowers/plans/climaprev-backend-mvp.md`
7. `.superpowers/sdd/climaprev-backend-mvp/task-9-report.md`
8. `.superpowers/sdd/climaprev-backend-mvp/task-9-review.md`

## Processo na próxima retomada

Siga esta sequência quando o usuário autorizar a retomada:

1. Reabra o workspace `C:\Users\sammt\OneDrive\Documentos\ClimaPrev`.
2. Leia este handoff e os documentos de referência acima.
3. Confirme o estado pausado e o último resultado validado.
4. Aguarde o usuário definir e aprovar o próximo escopo.
5. Crie um brief específico antes de alterar código ou testes.
6. Aplique TDD, implemente com subagentes e execute os testes dentro do Docker.
7. Solicite revisão independente entre as tasks e corrija achados antes de
   avançar.
8. Atualize o relatório da task, `progress.md`, `.specs/STATE.md` e este
   handoff com evidências reais.
9. Pare containers temporários ao finalizar a sessão.

Não iniciar trabalho novo nem despachar subagentes antes da confirmação
explícita do usuário. Não remover volumes, imagens ou arquivos do projeto.

## Git na próxima retomada

O Git passa a fazer parte do fluxo de trabalho a partir da próxima sessão.
Depois de reabrir o terminal, verifique a instalação e o estado do repositório:

```powershell
git --version
git status --short --branch
```

Se `git` ainda não for reconhecido, reabra o terminal para atualizar o `PATH`
antes de continuar. Quando houver um repositório válido, crie ou selecione uma
branch de trabalho, revise o diff e use staging explícito por allowlist.

Não usar `git add .`. O diretório `.specs/` é material de planejamento e
contexto e não deve entrar na lista de arquivos a subir: nunca deve ser
adicionado ao staging, commit ou push. Antes de qualquer commit, conferir:

```powershell
git diff --cached --name-only
```

Se qualquer caminho `.specs/` aparecer, removê-lo do staging e revisar a
allowlist. A revisão e o commit devem ocorrer somente após a confirmação
explícita do próximo escopo pelo usuário.

## Limitações conhecidas

O MVP ainda não inclui integração autorizada de alertas oficiais, autenticação,
histórico persistente, notificações, mapas, frontend, aplicativo mobile ou ML.
O baseline usa um mock determinístico e não representa disponibilidade do
Open-Meteo público nem capacidade de produção.

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
