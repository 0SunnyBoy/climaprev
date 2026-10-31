# Relatório de Pendências (RDP) — ClimaPrev

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 19/10/2026. Branch local: develop. Referência: commit 23bf4ce e alterações locais ainda sem commit.

## Parecer

### Estado vigente após catálogo espacial

Atualização seguinte: diagnóstico horário dos 37 registros altos relevantes concluído e valores reconciliados; inventário local registra 114 snapshots conhecidos, 14 artefatos de testes e nenhuma correspondência conhecida com reservas. Não certifica ausência de acesso anterior/externo. 88 testes direcionados aprovados, Ruff e mypy do módulo novo aprovados. Restam revisão científica/proveniência das reservas, decisões de aceite e protocolo prospectivo final. [Detalhes atuais](../planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md).

Coleta espacial concluída: 72 snapshots, 180 estratos e 30 agregações. Catálogo novo reconstruiu 3.747 casos, reconciliou todos os 180 estratos e verificou conjunto/parametrização dos snapshots. Os altos observados concentram-se em seis unidades local/data; nenhum braço recuperou sua detecção. Calor moderado tem mais detecções e também mais falsos alarmes na consulta da estação. Não há base para promover essa configuração automaticamente.

Regressão deste incremento: 85 testes direcionados aprovados, Ruff e mypy do módulo novo aprovados. A suíte completa anterior de 574 testes não foi repetida. As seções cronológicas abaixo preservam estados anteriores; pendências antigas de implementação do bootstrap/coleta espacial foram superadas tecnicamente, mas aprovação científica continua pendente.

Próximos itens: diagnóstico horário dos casos existentes de 2024; auditoria de proveniência das reservas sem abrir outcomes; definição científica dos critérios e responsável; eventual nova versão prospectiva do protocolo. Etapa 6/fitting/calibração/promoção permanecem bloqueados. [Diagnóstico e adendo vigente](../planejamento/reference-candidate-1/diagnostico-e-adendo-2026-10-19.md).

A aplicação funciona localmente com Docker, API, interface e Redis. A última regressão completa aprovada registrou 574 testes de back-end e os 10 testes de front-end anteriormente aprovados, build/typecheck, ESLint, Ruff (com EXE002 ignorado) e mypy. O último lote alterou somente ferramentas offline, testes e documentos; não repetiu checks de frontend sem mudanças. A primeira tentativa teve um timeout Redis, preservado no registro operacional; a repetição na imagem construída passou sem exclusões. Isso não equivale a homologação completa ou aprovação científica de uma nova política.

### Avanços da execução deste RDP

- Obtidos CSVs oficiais de 2024 para A201/A001/A801 e executados 72 relatórios nos 36 snapshots. A síntese usa os mesmos dias D+1/D+3/D+7: 252 unidades local/data de chuva, 249 de rajada e 248 de cada extremo térmico. Aceite científico continua pendente.
- Implementados auditor mensal, fronteira anual, suporte observacional e bootstrap. A continuação reconciliou numericamente os três valores de chuva publicados para Belém pelo dia encerrado às 12 UTC. Não houve inferência aprovada ou ajuste de candidata. Detalhes em [reconciliação e suporte](../planejamento/reference-candidate-1/reconciliacao-e-suporte-2026-10-19.md).
- Corrigidos idioma da mensagem de sucesso, erro/repetição da busca e reconsulta de cache de alertas stale/expirado. Esses incrementos não encerram acessibilidade ou a validade/cobertura completa dos alertas.
- Configurados ESLint, Vitest e auditoria Node na CI; verificações locais aprovadas. Execução remota e checks obrigatórios ainda pendentes.
- Homologação local: topologia, hardening, fronteira HTTPS, CA/logs, Redis e rotação sintética aprovados. Scanner fixado pelo projeto sem achados no limiar HIGH/CRITICAL; ressalva sobre metadados EOL do Alpine registrada na evidência.
- Teste de tema passou a aguardar condição observável do DOM, preservando as asserções. Gate de navegador ainda não executado: duas obtenções do runner fixado falharam com `unexpected EOF` na camada de 841.952.792 bytes. Não declarar esse gate aprovado.
- README, estado, roadmap, handoff e catálogo técnico atualizados. O PDF acadêmico permanece inalterado.
- Estágio de carga construído e cinco smokes no mock aprovados após aguardar readiness. A tentativa inicial com falhas de startup foi preservada. Ainda falta medir capacidade sustentada em ambiente dedicado; os smokes não encerram F10.
- Baseline descritiva completada para os cinco eventos: 15 agregações e 180 estratos. Chuva horária pareada em 36 relatórios e 252 unidades local/data por horizonte, sem detecção GFS dos dois dias altos observados. Mantêm-se os diagnósticos de chuva diária e rajada. É avaliação de limiares sobre agregados experimentais, não reprodução integral da API. [Pareamento e evidências atuais](../planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md); critérios e aprovação científica continuam pendentes.

Detalhes e proveniência em [execução técnica de 19/10](../planejamento/reference-candidate-1/execucao-2026-10-19.md) e [validação operacional](../operacoes/validacao-local-2026-10-19.md). A ordem abaixo é preservada; itens já implementados dependem apenas dos aceites ainda descritos.

A prioridade para evoluir a previsão continua sendo concluir a preparação da reference-candidate-1 com observações confiáveis. A reference-v1 permanece ativa. Ajustar classificação, calibrar coeficientes e promover candidata são atividades futuras, fora da autorização atual das etapas 1 a 5.

## Pendências encerradas ou parcialmente atendidas

| Item | Estado atualizado |
| --- | --- |
| Instalação e funcionamento local do Docker | Resolvido; serviços iniciados e endpoints de saúde verificados. |
| Git e vinculação ao histórico | Resolvido na cópia atual; develop no histórico original. Persistem mudanças locais sem commit. |
| Obtenção do CSV oficial A201/Belém | Resolvido; identidade, integridade e formato real validados. |
| Comparações observacionais do piloto | Executadas para janeiro/2025 em D+1/D+3/D+7, incluindo chuva, temperatura e rajada. Aceite científico permanece aberto. |
| Ampliação inicial de dados | 36 snapshots de 2024 em três locais; 261 unidades local/data pareadas. Ainda não representa expansão observacional suficiente. |
| Ferramentas de avaliação e rastreabilidade | Cobertura, auditorias, comparadores e congelamento técnico implementados. Não declarar o aceite científico concluído. |
| Evidências visuais do relatório | Prints reais incluídos no PDF de 19/10. |
| Testes e verificações locais | Aprovados no lote de 19/10; navegador automatizado, TLS e carga não foram executados nesse lote. |
| Dependências de desenvolvimento Python | Lock já existe na develop; manter reprodução e consistência. Não permanece válida a antiga afirmação de ausência desse lock. |

## Ordem recomendada de trabalho

### 1. Aprovar a adequação da referência observacional — prioridade alta

- Reconciliação numérica concluída: 417,0 mm com encerramento às 12 UTC e fronteira anual. O total civil de 427,6 mm e o UTC nominal de 427,0 mm representam outras janelas. Resta revisar e aprovar a adequação científica da fonte, sem confundir essas convenções.
- Registrar versão da fonte, convenção temporal, qualidade e eventuais revisões, sem alterar artificialmente os dados para igualar totais.
- Revisar representatividade espacial: grades a aproximadamente 10,333 km (GFS) e 11,958 km (ERA5) da estação. Se necessário, criar experimento complementar nas coordenadas da estação, preservando o original.
- Validar a comparabilidade de temperatura instantânea, extremos horários e rajadas entre as fontes.

**Aceite:** referência e convenções justificadas, limitações documentadas e revisão científica registrada. Depende de investigação das fontes; não é só implementação de código.

### 2. Completar a base observacional e avaliar suficiência — prioridade alta

- Obtenção e execução observacional concluídas tecnicamente em 19/10 para as janelas de 2024. Resta aprovar qualidade instrumental, representatividade e metadados históricos das estações.
- Reavaliar diversidade regional/sazonal e suporte por evento/classe. Na expansão com ERA5 há apenas dois dias classificados como chuva diária alta e nenhum evento alto nos outros tipos; isso não sustenta otimização de alto risco.
- Qualquer ampliação adicional deve ser previamente especificada, sem selecionar períodos porque favorecem resultados.

**Aceite:** amostra observacional com cobertura e suficiência avaliadas conforme critérios previamente definidos. O piloto de 31 dias não encerra esta etapa.

### 3. Fechar o protocolo e a integridade das reservas — prioridade alta

- Identificar revisor e aprovar evento/métrica principal, suporte mínimo, precisão desejada, ganho mínimo e tradeoffs de falsos alarmes.
- Registrar que o CSV anual de 2025 foi obtido e processado estruturalmente, incluindo meses reservados; apenas janeiro teve métricas examinadas nesta execução. Revisar a independência da reserva antes de alegá-la.
- Bootstrap por blocos implementado e testado em 19/10; falta aplicar inferência científica após definir e aprovar métrica/população e resolver a adequação das fontes.
- Versionar protocolo e manifestos atualizados sem sobrescrever os congelamentos anteriores.

**Aceite:** critérios e partições auditáveis definidos antes de ajustar candidata; aprovação científica explícita.

### 4. Congelar alvos observacionais e consolidar a baseline — prioridade alta

Avanço: métricas diagnósticas da v1 disponíveis para cinco eventos, com estratos,
matrizes e suporte explícito. Os segmentos temporais têm 3/28/28/28 dias; o primeiro
é menor que o bloco primário de sete dias, impedindo publicar intervalo pela regra
atual. Não houve exclusão retroativa de janeiro para contornar essa limitação.
Alvos científicos e inferência aprovada permanecem abertos. O pareamento de máximos
de chuva horária foi concluído tecnicamente, com avaliação diagnóstica e suporte explícito.

- Após validar a referência, gerar e versionar alvos por evento com os limiares atuais da reference-v1, independentes da candidata.
- Distinguir alvos de estação, rótulos de reanálise e observações de impactos; não tratá-los como equivalentes.
- Consolidar avaliação da v1 por classe, evento, região e antecedência, com denominadores, exclusões e incerteza.
- Preservar hashes, dados elegíveis, configuração e execução reproduzível.

**Aceite:** baseline e alvos rastreáveis, adequados ao protocolo. Não inclui escolher novos limiares.

### 5. Concluir qualidade funcional e homologação — alta antes de entrega pública

| Frente | Trabalho restante | Critério de encerramento |
| --- | --- | --- |
| Tema e navegador (F09) | Reproduzir a falha histórica na verificação de tema; corrigir comportamento/sincronização conforme diagnóstico; executar gate completo. | Tema, persistência, navegação e demais verificações aprovados no runner da versão. Alternância manual não encerra o gate. |
| CI (F07) | Lint/Vitest/auditoria Node configurados e exercitados localmente; validar no GitHub e revisar consistência dos locks/checks obrigatórios. | Checks de promoção executados e política de bloqueio verificável. Execução local não substitui execução remota. |
| Datas (F01) | Definir suporte temporal por fuso e aplicar limites coerentes na API/UI antes da chamada externa. | Fronteiras, passado, hoje, último dia válido e viradas de fuso cobertos. |
| Alertas (F04) | Rever expiração na entrega/cache, stale, validade dos avisos, cobertura parcial e geometrias. Diagnosticar a indisponibilidade observada. | Não confundir fonte indisponível ou cobertura incompleta com ausência de alertas. |
| Prazo da consulta (F05) | Coordenar prazo global entre interface, chamadas externas, retries e espera de lock; avaliar concorrência após localização. | Lentidão, cancelamento e contenção respeitam o contrato, com limpeza e fallback válidos. |
| Busca e acessibilidade (F11) | Erro, lista vazia e repetição implementados/testados; concluir leitor de tela, teclado, contraste, rede lenta e viewport móvel. | Fluxos e falhas verificados com evidências. |
| Idioma | Mensagem de sucesso corrigida e coberta por regressão em 19/10; revisar os demais estados na homologação completa. | Mensagens e resultado acompanham o idioma selecionado. |
| Retorno da emergência | Revisar formulário vazio com resultado anterior preservado e definir o comportamento desejado. | Decisão de experiência registrada e comportamento coerente; ainda não classificado como defeito confirmado. |
| Segurança/homologação | TLS, rotação sintética, scan runtime e regressão local executados em 19/10; concluir navegador e aceite final da versão. | Evidências completas da revisão escolhida; sem depender apenas de resultados históricos. |

Os itens desta etapa podem avançar enquanto se resolvem dependências científicas das etapas anteriores. A prioridade científica não impede corrigir falhas funcionais independentes.

### 6. Medir operação e preparar publicação — condicionada ao aceite

- F06: agregar métricas entre processos/réplicas, retenção externa, painéis, alertas, metas e responsáveis.
- F10: executar carga em ambiente dedicado, com versão, recursos, cenários, quotas, erros e percentis registrados; separar capacidade interna da disponibilidade de provedores públicos.
- F08: definir ambiente/operador, DNS/TLS, segredos, promoção, readiness e recuperação; demonstrar monitoramento e rollback.
- F12: alinhar README, planejamento, runbooks e pacote de contexto ao commit final, resultados e limitações; preservar documentos antigos como históricos.
- Revisar e organizar o diff local antes de eventual commit/push. Nenhum envio foi realizado nesta atualização.

**Aceite:** versão identificável, gates aprovados, acesso e operação verificados, rollback demonstrado. Docker local funcionando não comprova publicação pronta.

### 7. Evoluir a política — futura autorização e evidência

Somente depois do aceite científico das etapas 1 a 5 do plano original e de nova autorização: executar experimentos separados de classificação e calibração, comparar com a v1 e decidir manter baseline ou promover candidata. A numeração deste RDP é uma ordem de trabalho e não substitui a numeração do protocolo original; a etapa 6 original de ajuste continua não iniciada.

Se houver promoção, revisar seleção/configuração da política, identidade e fallback, testes de fronteira, contrato da API, apresentação PT/EN, proveniência da calibração quando aplicável, cache, métricas, documentação e rollout/rollback. Não substituir globalmente referências históricas à v1. Uma nova política de risco não demonstra, por si só, melhoria dos valores meteorológicos previstos.

## Fontes e limites

Consolidação dos relatórios de pendências e revisão da develop de 15–16/10, da revisão das implementações com CSV, do planejamento reference-candidate-1 e da validação local de 19/10. Os relatórios antigos contêm estados históricos superados, identificados acima.

Na consolidação inicial deste RDP foram conferidos arquivos locais, status Git, planejamento e workflows. Sua execução posterior acrescentou as consultas oficiais INMET, comparações, testes e checks operacionais registrados nos documentos de 19/10. Não houve nova consulta ao GitHub, commit/push, deploy público ou auditoria completa de segurança. O RDP não atesta que a branch remota permanece sem atualizações posteriores à última consulta.

### Incremento espacial — 19/10/2026

Plano espacial congelado em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md e evidence/plano-espacial-2024-2026-10-19.json: 72 snapshots previstos, com controle municipal novo e braço nas coordenadas INMET de 2024, altitude e seleção de célula fixas por par. Sete testes novos aprovados, mypy aprovado. Coletor, preflight do provedor, coleta e comparação ainda pendentes; nenhum resultado espacial ou ganho de previsão declarado. Mantidos reference-v1 ativa e bloqueio de fitting/etapa 6.

### Execução espacial concluída — 19/10/2026

O incremento espacial anterior avançou: coletor e pareamento implementados, preflight real aprovado, 72 snapshots coletados sem falhas, 180 estratos e 30 agregações comparados, sem perda adicional dos dias elegíveis anteriores. Os resultados são mistos; nenhuma detecção dos altos de chuva horária/diária/rajada foi recuperada e a temperatura mínima teve MAE maior nos três horizontes. Reference-v1 mantida, sem fitting ou promoção. Próximo incremento: catálogo dos casos altos perdidos e falsos alarmes, seguido de consolidação dos limites e critérios científicos. Detalhes e evidências em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md. As pendências de coletor/coleta citadas no registro anterior estão concluídas.
