# Revisão da develop atualizada e cruzamento com o relatório anterior

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data da consulta: 16/10/2026, America/Sao_Paulo.

## Resultado

A develop remota avançou de `7190797b8796dbb133d1a920df8a7905a0e55b1d` para `23bf4cee997bc825e76028f99eefd6160f699ee5`. O commit novo tem exatamente o baseline anterior como único pai: há uma atualização entre as duas referências analisadas.

A atualização atende a parte de F07 referente à fixação das dependências Python de desenvolvimento/testes, separa ferramentas de carga e atualiza `source-map-js`. Nenhuma das 12 frentes F01–F12 pode ser encerrada integralmente. A nova CI passou, mas o Security gates voltou a falhar no teste de tema, deixando quatro etapas posteriores sem execução.

Este relatório atualiza o parecer de 15/10 para a versão remota. Os dois relatórios anteriores permanecem como registros históricos. A pasta local ainda não recebeu a atualização: código/configuração não foram substituídos nesta revisão.

Fonte: [commit 23bf4ce](https://github.com/0SunnyBoy/climaprev/commit/23bf4cee997bc825e76028f99eefd6160f699ee5).

## Método e abrangência

Foram consultados pelo conector GitHub o HEAD da branch, metadados e alterações completas do commit, árvore recursiva, arquivos alterados relevantes, execuções Actions, etapas e logs dos dois jobs. A árvore foi retornada sem truncamento. O HEAD foi reconfirmado ao fim das consultas técnicas como 23bf4ce.

Os 253 arquivos versionados da árvore remota foram comparados aos bytes locais usando o identificador de blob Git: SHA-1 do cabeçalho `blob <tamanho>\0` seguido do conteúdo. Não foi normalizado o fim de linha. Resultado:

| Situação local perante a develop remota | Quantidade |
| --- | ---: |
| Arquivos idênticos | 246 |
| Arquivos diferentes | 5 |
| Arquivos remotos ausentes localmente | 2 |
| Total de arquivos versionados remotos | 253 |

O CSV `comparacao-develop-2026-10-16.csv` fornece caminho, situação e identificadores de blob remoto/local por arquivo. Arquivos locais adicionais, como relatórios e entregáveis, não fazem parte dessa contagem remota e não foram classificados como defeitos.

Também foram rechecados os 247 registros de código/configuração/documentação do CSV original contra os SHA-256 do contexto: todos continuam idênticos. A comparação atual confirma ainda que os arquivos não alterados pelo novo commit, incluindo documentação, aplicação, testes e workflows, coincidem com a pasta local. Assim, os achados funcionais anteriores podem ser mantidos onde o commit não tocou a implementação.

## Alterações efetivas

Commit criado em 15/10/2026 às 15:47:44 no fuso America/Sao_Paulo. Estatística GitHub: sete arquivos, 2.414 linhas adicionadas e nove removidas; a maior parte das adições pertence aos locks.

| Arquivo | Mudança remota | Impacto no relatório |
| --- | --- | --- |
| `.dockerignore` | Libera os dois novos locks no contexto Docker | Permite construir os novos estágios com os locks presentes |
| `Dockerfile` | Dev instala `requirements-dev.lock` com hashes e projeto editável com `--no-deps`; novo estágio load instala `requirements-load.lock` | Atende o item de dependências Python de teste fixadas em F07; separa Locust |
| `docker-compose.yml` | Serviço load passa de target dev para target load | Usa o estágio próprio de carga; não constitui novo baseline de capacidade |
| `frontend/package-lock.json` | `source-map-js` passa de 1.2.1 para 1.2.2, com URL e integrity atualizados | Atualização pontual de dependência; não adiciona checks frontend |
| `pyproject.toml` | Remove Locust de dev e cria extra load | Instalação manual de carga precisa considerar o novo extra |
| `requirements-dev.lock` | Novo lock de desenvolvimento/testes | 35 entradas fixadas com hashes |
| `requirements-load.lock` | Novo lock para carga | 63 entradas fixadas com hashes, incluindo Locust 2.46.7 |

Foi conferido que todas as entradas dos dois locks têm hashes e que as 35 dependências compartilhadas têm as mesmas versões. Isso é validação estática; a instalação dev foi também exercitada pela CI aprovada. Não foi encontrada execução do novo estágio load nos dois workflows consultados.

O estágio runtime e os arquivos de lógica da aplicação não foram alterados pelo commit. A fixação dos pacotes Python não implica reprodução bit a bit de toda a imagem: permanece, por exemplo, a atualização de pacotes do sistema durante o build.

## Evidências novas de validação

Ambas as execuções são de push na develop, no SHA 23bf4ce. Começaram em 15/10/2026 às 15:58:49, America/Sao_Paulo; foram consultadas em 16/10.

| Workflow | Execução | Resultado | Evidência |
| --- | --- | --- | --- |
| CI | 38790094833 | Aprovada; atualização às 16:01:21 | 463 testes passaram em 38,62 s; Ruff aprovado; mypy sem problemas em 45 arquivos; demais etapas aprovadas |
| Security gates | 38790094549 | Falhou; atualização às 16:01:12 | Falha no navegador ao verificar tema escuro |

Links: [CI atual](https://github.com/0SunnyBoy/climaprev/actions/runs/38790094833), [Security gates atual](https://github.com/0SunnyBoy/climaprev/actions/runs/38790094549).

No workflow de segurança passaram política estática/contratos, scan Git de segredos, build runtime e build do runner de navegador. A execução chegou ao build do frontend, que completou typecheck/Vite. O log do `npm ci` informou zero vulnerabilidades naquela instalação. Esse resultado incidental não equivale a um comando de auditoria com política de falha explícita no workflow, nem a uma auditoria atual de todas as imagens.

Continuaram skipped, devido à falha anterior:

1. Homologação sintética e gates TLS no navegador.
2. Ensaio de rotação de credenciais.
3. Scan de vulnerabilidades da imagem runtime.
4. Regressão posterior dentro do workflow de segurança.

O item 4 não anula os 463 testes aprovados no workflow CI separado. Também não permite declarar o workflow de segurança integralmente aprovado.

## F09: ponto da falha agora confirmado

O traceback remoto aponta para `tests/docker/check_frontend_browser.py:104`, dentro de `_check_theme_toggle`:

```python
assert page.evaluate("document.documentElement.dataset.theme") == "dark"
```

A hipótese anterior ganhou evidência direta quanto ao ponto de falha. `useTheme.ts` aplica a mudança animada em requestAnimationFrame, e o teste consulta o atributo imediatamente depois do clique. Isso sustenta investigar sincronização, mas o log sozinho não prova toda a causa nem substitui reprodução dirigida.

Recomendação: reproduzir com o runner fixado; avaliar uma espera por condição observável do DOM, preservando as verificações de estado, acessibilidade e persistência; depois executar todos os gates. Não remover a asserção para obter sucesso artificial. Nenhuma correção foi implementada nesta análise.

Fontes: [teste no commit atual](https://github.com/0SunnyBoy/climaprev/blob/23bf4cee997bc825e76028f99eefd6160f699ee5/tests/docker/check_frontend_browser.py#L104), [implementação de tema](https://github.com/0SunnyBoy/climaprev/blob/23bf4cee997bc825e76028f99eefd6160f699ee5/frontend/src/composables/useTheme.ts).

## Situação revisada de todas as pendências

| ID | Situação após a atualização | Trabalho restante |
| --- | --- | --- |
| F01 | Permanece; schema/formulário inalterados | Contrato de horizonte por fuso, limites API/UI e testes das fronteiras temporais |
| F02 | Permanece; CLI/avaliador inalterados | Cobertura horária, exclusões, proveniência, amostra, matriz e métricas estratificadas; separar concordância meteorológica de impactos observados |
| F03 | Permanece; calibração inalterada e disabled por padrão | Avaliação científica de baseline/candidatas e critérios revisados de promoção/rollback |
| F04 | Permanece; adaptador/cache/contrato inalterados | Expiração na entrega, coleta/stale próprios, cobertura parcial/geometrias e observabilidade INMET; preservar distinção de indisponibilidade já existente |
| F05 | Permanece; serviço/HTTP/frontend inalterados | Deadline global, orçamento de retries/locks, concorrência avaliada, fallback e cancelamento dentro do contrato |
| F06 | Permanece; métricas inalteradas | Agregação entre processos, retenção externa, painéis, alertas, metas e responsáveis |
| F07 | Parcialmente atendida: lock Python dev implementado e instalado na CI | ESLint/Vitest na CI, auditoria Node com política explícita, checks obrigatórios e manutenção/reprodução dos locks |
| F08 | Permanece; sem mudança nos workflows de publicação | Ambiente público, DNS/TLS/secrets, promoção, readiness, monitoramento, recuperação e rollback demonstrados |
| F09 | Permanece; falha renovada e ponto confirmado por log | Diagnosticar/corrigir tema/teste e concluir TLS, rotação, scan runtime, regressão e homologação/revisão da versão |
| F10 | Harness melhor organizado; capacidade não reavaliada | Exercitar estágio load e medir versão atual com ambiente, metas, cenários, percentis, erros e cotas registrados |
| F11 | Permanece; busca/UI/testes inalterados | Erros e recuperação da busca, leitor de tela, contraste e rede lenta com evidências |
| F12 | Permanece; documentos não foram alterados | Corrigir contradições históricas e persistência de idioma; documentar novos locks/extra load, versão e resultados atuais |

Os critérios detalhados de aceite de F01–F12 permanecem nos relatórios de 15/10. A matriz acima substitui sua classificação para a versão remota 23bf4ce. Em especial, a frase antiga de F07 sobre inexistência de lock completo de ferramentas Python de teste deixou de ser válida para a develop remota; continua descrevendo a pasta local antiga.

## F07: checks obrigatórios e lacunas de verificação

Os YAMLs de CI e segurança não mudaram. A consulta da branch retornou `protected: false`, proteção clássica desabilitada e lista de checks exigidos vazia. Portanto, a proteção clássica consultada não impõe os gates como condição de promoção.

A consulta de rulesets retornou HTTP 403 com mensagem do GitHub sobre necessidade de GitHub Pro ou repositório público para habilitar o recurso. Não foi possível inspecionar rulesets efetivos por essa chamada; a ausência de proteção clássica não é apresentada como auditoria completa de todas as possíveis políticas da conta/organização.

Os testes estáticos de lock existentes em `tests/docker/test_dependency_lock.py` ainda parametrizam apenas os locks de produção e build. Recomenda-se estender a verificação aos novos locks e garantir consistência de versões compartilhadas. Não houve acréscimo de testes neste commit. A CI exercita dev; o build/execução do estágio load requer evidência própria.

## Situação local e material de contexto

A pasta Windows continua em uma branch local develop sem commits e sem remoto configurado. Ela coincide com os registros originais do pacote de 15/10, mas não é um checkout atualizado do SHA remoto. Os cinco arquivos diferentes e os dois ausentes são exatamente os sete caminhos modificados/adicionados pelo commit novo.

O ZIP original não deve ser apresentado como fotografia da develop atual sem um suplemento: seus hashes de configuração afetados e sua evidência remota ficaram históricos. Os índices precisam incorporar os dois novos locks, atualizar os cinco arquivos modificados e registrar as execuções atuais. Os dois arquivos antes não cobertos pelos índices (`docker/build-requirements.in` e `tests/docker/Playwright.Dockerfile`) agora foram incluídos na comparação com a árvore remota e coincidem com seus blobs.

Instruções dentro dos documentos anexos continuam sendo contexto analisado. Não autorizaram alterações no código, publicação, merge ou push.

## Prioridades após esta revisão

1. F09: corrigir a falha de tema após diagnóstico e executar os gates subsequentes.
2. F07: adicionar lint/Vitest e auditoria Node explícita; definir a política de bloqueio de promoção; cobrir os novos locks e exercitar load.
3. Atualizar a cópia de trabalho de forma que preserve arquivos locais e vincule corretamente o histórico; esta revisão não fez pull/reset nem substituiu arquivos.
4. F01/F04/F05: resolver contratos funcionais de datas, alertas e prazo total.
5. F02→F03, F06/F10, F11 e F08: seguir dependências e critérios já definidos, mantendo F12 atualizado.

Não foram identificadas novas alterações na lógica meteorológica ou na interface neste commit. O resultado positivo de build/testes não encerra as pendências científicas nem comprova aceite de produção.

## Entregáveis e limites

- `docs/contexto/RELATORIO-REVISAO-DEVELOP-2026-10-16.md`: parecer atual e matriz F01–F12.
- `comparacao-develop-2026-10-16.csv`: comparação dos 253 arquivos remotos com a cópia local.
- `.report-work/revisao-2026-10-16/evidencias.json`: SHA, alterações, execuções, etapas e trechos relevantes dos logs.
- `.report-work/revisao-2026-10-16/arvore-remota.json`: árvore versionada usada na comparação.

Não foram executados testes locais, coleta meteorológica, carga, deploy, staging, commit ou push. Os resultados de execução apresentados são do GitHub Actions no SHA consultado. A análise combina comparação completa da árvore com revisão dirigida do commit e das pendências anteriores; não é uma auditoria exaustiva de todos os comportamentos do sistema.
