# Validação local do ClimaPrev em 19 de outubro de 2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Encerramento das pendências históricas — 20/10/2026

As limitações de navegador/carga abaixo se referem aos lotes de 19/10. Posteriormente, gate JS/Edge HTTPS entre origens distintas e campanha local de cinco cenários foram concluídos; 644 testes backend/27 frontend aprovados. Isso não afirma execução completa do runner Python fixado, leitor de tela manual, capacidade de hospedagem ou aprovação da CI remota atual.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Continuação posterior — chuva horária e cinco eventos

Foram adicionados máximo horário civil na auditoria, comparador de estação e
classificação diagnóstica de chuva horária com os limiares atuais. Os 36 pais e
CSVs preservados foram conferidos por hash; a interseção de 252 unidades local/data
de chuva foi mantida. A baseline e o preflight agora cobrem cinco eventos, com
15 agregações e 180 estratos. Os resultados de quatro eventos anteriores permanecem
como pai; não foram silenciosamente sobrescritos.

Os 13 testes dirigidos de auditoria/comparadores/baseline passaram. Ruff aprovado
com EXE002 ignorado e mypy aprovado nos 61 arquivos de origem. Na primeira regressão
geral, 573 testes passaram e um falhou por timeout na conexão Redis do harness;
o Redis respondeu PONG no diagnóstico seguinte. A imagem foi reconstruída para
repetir a suíte sem o bind mount Windows. Esse resultado inicial é preservado,
sem remoção de teste ou alteração de timeout para produzir aprovação artificial.

A repetição na imagem construída foi aprovada: **574 testes passaram**, com
warnings como erro, sem exclusões, em 47,58 s. Apenas um contêiner de regressão
foi mantido durante essa repetição, usando Redis DB 15. A API continuou separada.

Não houve nova coleta, consulta de períodos reservados, ajuste de limiares,
calibração, nova execução de frontend, carga, scanner ou navegador. O endpoint
de prontidão local permaneceu `ready`. O PDF acadêmico não foi alterado.
Ver [chuva horária e evidências atuais](../planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md).

## Continuação posterior — baseline diagnóstica por evento

O novo avaliador offline foi executado nas datas comuns D+1/D+3/D+7, gerando
12 agregações e 144 estratos para quatro eventos. Seus seis testes verificam
matrizes, falsos alarmes, subestimação, ausência de suporte, duplicatas e valores
inválidos. Não houve ajuste ou reprodução integral da API; chuva horária permanece
explicitamente omitida até haver pareamento dos máximos de modelo.

Regressão completa: **570 testes passaram**, warnings como erro, em 103,49 s no
contêiner isolado com código atual via bind mount e Redis DB 15. Ruff aprovado com
EXE002 ignorado; mypy aprovado nos 60 arquivos de origem. Interface inalterada,
sem repetição dos seus dez testes do lote anterior. `/health/ready` local respondeu
`ready`; nenhuma nova imagem, carga, homologação ou promoção neste lote offline.

O preflight e a proposta de critérios registram os bloqueios de suporte e de
segmentos curtos, mantendo a aprovação científica e a autorização de ajuste falsas.
Ver [baseline e critérios propostos](../planejamento/reference-candidate-1/baseline-e-criterios-propostos-2026-10-19.md).

## Continuação posterior — reconciliação e suporte observacional

As ferramentas offline receberam agrupamento diário, fronteira anual para o dia
encerrado às 12 UTC e contagem de suporte da estação nas datas elegíveis de 2024.
Resultado: **564 testes passaram** com warnings como erro em 105,60 s, em contêiner
de testes com bind mount do código atual, Redis DB 15 e API separada. Ruff aprovado
com EXE002 ignorado e mypy aprovado nos 59 arquivos de origem.

O frontend não foi alterado; seus 10 testes e demais checks do lote anterior
continuam como evidência daquela execução. Não houve nova construção de imagem,
execução de carga, scanner ou homologação neste lote offline. A ferramenta atual
pode ser executada com PYTHONPATH=src no checkout; para utilizá-la dentro de uma
imagem sem bind mount, reconstruir a imagem com o código atual.

O dia encerrado às 12 UTC e a fronteira de dezembro reproduziram 417,0 mm no mês,
384,4 mm até 30/01 e 56,2 mm em 09/01. A adequação científica permanece pendente;
não houve mudança nos alvos civis, política ativa, coeficientes ou PDF acadêmico.
Consulte [reconciliação e suporte](../planejamento/reference-candidate-1/reconciliacao-e-suporte-2026-10-19.md).
O endpoint de prontidão local continuou respondendo `ready` ao encerrar.

## Continuação — execução do RDP

O registro inicial abaixo permanece como histórico do primeiro lote. A versão
local atual recebeu as correções de idioma, busca e cache de alertas descritas na
[execução técnica](../planejamento/reference-candidate-1/execucao-2026-10-19.md).

- Regressão na imagem construída: **555 testes passaram**, com warnings como erro,
  em 40,03 s. O contêiner de testes é exclusivo e usa Redis DB 15.
- Frontend: **10 testes em 6 arquivos passaram**; ESLint, build/typecheck aprovados.
- Ruff aprovado com EXE002 ignorado; mypy aprovado nos 58 arquivos de origem.
- `npm audit --audit-level=high` retornou zero vulnerabilidades.
- Os oito testes de contratos Docker passaram após o ajuste do gate de tema;
  o script preserva as asserções e agora espera o estado do DOM após cada clique.
  O teste sintético distingue `method=forecast_heuristic` de `policy_version=reference-v1`.
- A configuração de CI inclui lint, Vitest e auditoria Node, mas não foi enviada
  nem executada no GitHub neste lote.

### Homologação sintética

Provisionada a stack isolada `climaprev-homolog`, com runtime não root, Redis
autenticado e CA local explícita. Passaram topologia, hardening, proxy/assets/API,
aceitação da CA correta e rejeição de CA não confiável, ocultação de rotas internas,
sanitização/retenção dos logs e recuperação dos emissores após reiniciar o coletor.
O check Redis confirmou autenticação correta e rejeição de senha ausente/incorreta
e acesso a prefixo alheio.

O ensaio de rotação gerou credenciais novas em `.homolog/next/`: a senha antiga foi
rejeitada, a cota HMAC continuou compartilhada entre workers e hardening/proxy
passaram novamente com a nova CA. São segredos sintéticos locais, ignorados pelo
Git; não houve rotação de credenciais de serviços externos ou mudança no trust
store global.

O scan da imagem runtime com o Trivy fixado pelo workflow não encontrou achados
no limiar HIGH/CRITICAL. Evidência e hash do relatório completo em
`../planejamento/reference-candidate-1/evidence/scan-runtime-2026-10-19.json`.
O scanner avisou que Alpine 3.24 não consta em sua lista EOL; o resultado não
constitui comprovação de ciclo de vida ou auditoria completa de segurança.

O runner Playwright fixado por digest não foi obtido: duas transferências da
camada de 841.952.792 bytes terminaram com `unexpected EOF`, após 111.017.984 e
512.983.040 bytes recebidos, respectivamente. Portanto, os gates de navegador HTTP
e HTTPS continuam **não executados**, e a correção da espera do tema ainda precisa
ser confirmada nesse runner. Os checks TLS Python aprovados não substituem esses gates.

### Estágio e smokes de carga

Build do estágio `load` e dos serviços de mock aprovado. Foram executados os cinco
cenários warm_cache, cold_cache, lock_contention, slow_upstream e redis_latency,
com dois usuários, taxa nominal de uma requisição por segundo por usuário e dez
segundos por cenário, exclusivamente em redes internas com mock meteorológico.
Os cinco smokes com espera de readiness terminaram com código zero e sem falhas.

A tentativa inicial de warm_cache começou antes da aplicação estar saudável e
registrou quatro falhas de transporte em 22 requisições. Ela foi preservada;
as reexecuções passaram após `docker compose up -d --wait`. Os comandos do README
e do runbook foram corrigidos para aguardar saúde antes de usar `run --no-deps`.
CSV/logs em `.report-work/load-2026-10-19/`; resumo, hashes, percentis e recursos
Docker em [evidence/carga-smoke-2026-10-19.json](evidence/carga-smoke-2026-10-19.json).
O CSV usa a última amostra gravada pelo Locust e pode anteceder a contagem final
do console. Esses ensaios curtos em máquina compartilhada validam o harness;
não aprovam capacidade sustentada ou metas de produção.

### Particularidade Windows/OpenSSL

Como não havia OpenSSL instalado no host, foi usado um adaptador local ao
provisionador existente, preservando suas ACLs Windows. Os arquivos usados ficam
em `docs/operacoes/scripts/`: construir `openssl.Dockerfile` com a tag
`climaprev-openssl-test:local` e executar `provision_tls_with_container.py` a partir
da raiz, opcionalmente com o diretório recém-provisionado como argumento.

A chave TLS gerada dentro do contêiner manteve modo Linux 0600 apesar do chmod
Windows; isso fez a entrada Nginx terminar antes do primeiro smoke. Apenas
`server.key` e `server.crt`, gerados nesta sessão, receberam o modo 0444 esperado
pelo provisionador através do volume Docker. A pasta manteve ACL privada e a chave
da CA permaneceu restrita. Hardening e TLS passaram após essa correção. Não aplicar
essa operação a credenciais externas preexistentes.

O PDF acadêmico não foi atualizado. Limiares e coeficientes permanecem intactos;
aprovação científica, navegador completo, capacidade e publicação continuam pendentes.

Ao encerrar, as stacks auxiliares de carga e homologação foram paradas, mantendo
dados e credenciais de teste locais para reprodução. API, frontend e Redis de
desenvolvimento permaneceram ativos; `/health/ready` respondeu `ready` pela porta
8080. Para retomar a homologação após a rotação, usar o env-file de `.homolog/next/`.

## Registro inicial do primeiro lote

Redis, API e interface foram construídos e iniciados com `docker compose up -d --build app frontend`. As portas são restritas a 127.0.0.1: API 8000 e interface 8080. Os endpoints `/health/live` e `/health/ready` responderam HTTP 200 pela entrada do front-end.

## Verificações

- Back-end: **542 testes passaram** em contêiner exclusivo de testes, com Redis no banco 15.
- Interface: **5 testes em 4 arquivos passaram**; ESLint passou.
- Build Vue/TypeScript/Vite aprovado durante a construção da imagem.
- Ruff passou com EXE002 ignorado; mypy passou para 56 arquivos.
- A primeira execução de pytest dentro do contêiner que já executava a API teve quatro falhas de logging por disputa da porta 8000. A execução em contêiner separado eliminou o conflito e passou integralmente, sem mudar código.

Comando de testes isolados:

```powershell
docker compose run --rm --no-deps -e REDIS_URL=redis://redis:6379/15 app python -m pytest -q -p no:cacheprovider --basetemp=/tmp/pytest-retomada-isolada --tb=short
```

## Navegador e capturas

Foi consultada Belém, Pará, Brasil para 20 a 22/10/2026, com resposta real do Open-Meteo, risco moderado e dados completos. Os alertas oficiais estavam indisponíveis; a interface informou essa condição. A indisponibilidade não foi convertida em ausência de alerta.

Foram verificados manualmente tema claro/escuro, autocomplete, consulta, navegação à emergência e retorno, e alternância PT-BR/EN. Capturas em `.report-work/evidence-ui-2026-10-19/screenshots/`. São registros da interface Vue atual, não as imagens históricas anteriores à migração.

Limitação observada: ao alternar para inglês depois da consulta, a mensagem de sucesso já armazenada permaneceu em português, embora o resultado fosse traduzido. Corrigir a reatividade dessa mensagem em trabalho posterior. O retorno da emergência remonta o formulário vazio mantendo o resultado anterior; revisar a experiência antes de alterar esse comportamento.

O gate automatizado completo de navegador, a validação em viewport móvel, a homologação TLS e os testes de carga ainda não foram executados neste lote. A verificação manual do tema não encerra a falha histórica de sincronização do gate.

## Estado ao encerrar

Serviços mantidos em execução para uso local. Nenhum limiar ou coeficiente foi ajustado; não houve promoção de política nem commit/push. As pendências científicas de observação e suficiência permanecem separadas desta validação operacional.

## Plano espacial — verificação incremental

42 testes direcionados aprovados (plano espacial, campanha e importação INMET), com warnings tratados como erros; Ruff e mypy aprovados. Os sete testes novos estão incluídos nesses 42. A execução inicial no sandbox teve quatro erros de setup ao criar temporários (38 testes passaram); uma segunda tentativa restrita foi interrompida sem conclusão. A repetição fora dessa restrição passou integralmente em 0,34 s. Não foi repetida a suíte completa de 574 testes do lote anterior. Plano real gerado a partir dos três CSVs com hash validado; coleta espacial ainda não executada.

## Coleta e comparação espacial concluídas

Preflight real aprovado e manifesto completo com 72 snapshots, zero falhas; comparação gerou 180 estratos e 30 agregações, sem exclusão adicional. Regressão consolidada: 79 testes direcionados aprovados em 0,62 s, warnings como erros; Ruff aprovado e mypy aprovado nos três módulos espaciais. Não foi repetida a suíte completa de 574 testes do lote anterior. Resultados e limitações em docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md. Não houve fitting, calibração, promoção ou alteração de runtime/frontend neste lote.

## Catálogo espacial — validação

85 testes direcionados aprovados em 0,96 s, warnings como erros; Ruff aprovado e mypy do módulo error_catalog aprovado. Reconstruídos 3.747 casos com reconciliação dos 180 estratos. A primeira execução parou na igualdade direta entre tuplas em memória e listas JSON; corrigida para comparar digests canônicos, sem alterar valores ou evidência anterior. Reexecução concluída, catálogo imutável gravado. Nenhuma suíte completa adicional, fitting ou acesso novo a outcomes reservados. Revisões independentes conferiram hashes, resultados e decisões científicas faltantes.

### Diagnóstico horário e inventário local — 19/10/2026

Concluídos diagnóstico de 37 registros relevantes para alto, com perfis e recompostos conferidos, e inventário local de reservas: 114 snapshots conhecidos, 14 artefatos de testes, zero origem desconhecida e zero correspondência conhecida com períodos reservados. Isso não certifica independência das reservas nem ausência de acesso externo/anterior. 88 testes direcionados aprovados; Ruff e mypy do módulo temporal aprovados. Versões iniciais preservadas; evidências atuais com sufixo v2. Detalhes em docs/planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md. Próximos: revisão científica e proveniência, critérios de aceite e protocolo prospectivo final; etapa 6 bloqueada. Nenhuma alteração no PDF acadêmico.
