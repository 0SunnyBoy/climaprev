# Fontes e coleta experimental

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

**Continuação:** [coletores e normalização implementados e preflight pontual executado](../../operacoes/coleta-experimental-2026-10-23.md) depois desta seleção documental. Onze de doze combinações local/fonte normalizadas, sem comprovação de rodada ou precisão; os gates e limitações são registrados no relatório. As afirmações abaixo de ausência de HTTP/preflight descrevem o primeiro incremento, preservado como histórico da seleção.

Revisão documental em 23/10/2026, após [aprovação da direção](aprovacao-direcao-2026-10-23.md). Não é preflight ao vivo dos modelos nem implantação de novos provedores. Seleção técnica inicial; versão/identificador exato e campos precisam ser confirmados no endpoint antes da campanha.

## Fontes priorizadas

| Fonte e modelo | Papel | Justificativa e restrição | Próximo gate |
|---|---|---|---|
| Open-Meteo / GFS global, NOAA | Primeiro braço explícito | Histórico do projeto já usa GFS; comparar com o serviço atual, sem chamar GFS de reference-v1 | Confirmar identificador, rodada e campos no produto escolhido |
| Open-Meteo / IFS, ECMWF | Segundo braço explícito | Família global distinta; versões e resolução devem ser registradas, sem assumir que todo IFS seja o mesmo produto | Conferir produto, cadência e semântica dos extremos |
| Open-Meteo / ICON global, DWD | Terceiro braço, inicialmente exploratório | Horizonte documentado de cerca de 7,5 dias exige verificar se D+7 contém o dia local inteiro | Excluir horizonte incompleto sem extrapolar ou preencher |
| MET Norway / Locationforecast | Segundo provedor, braço exploratório | No Brasil a origem global é ECMWF; não contar como evidência independente do IFS apenas por vir de outra API | Preflight de campos/intervalos, arquivo prospectivo e atribuição |
| INMET instrumental | Referência observacional | CSVs e instrumentos de estação, sujeitos a qualidade/cobertura; feed de alertas não é observação de chuva | Aprovar convenções por variável |
| ECMWF direto | Alternativa técnica posterior | Ingestão em grade/formatos científicos amplia custo técnico sem garantir nova informação de origem | Só priorizar se resolver limitação concreta do intermediário |

GFS/IFS/ICON globais têm cobertura pertinente à pesquisa brasileira; produtos regionais europeus não entram como substitutos. Seleção inicial não é conclusão de que algum modelo prevê melhor neste projeto. Referências de cobertura/produtos: [Open-Meteo Forecast](https://open-meteo.com/en/docs), [GFS](https://open-meteo.com/en/docs/gfs-api), [IFS](https://open-meteo.com/en/docs/ecmwf-api), [ICON](https://open-meteo.com/en/docs/dwd-api).

## Condições de uso

O endpoint gratuito Open-Meteo é para uso não comercial, com limites publicados; dados abertos não eliminam a condição de acesso ao serviço. Doação voluntária é permitida, mas integração vendida, publicidade e promoção comercial precisam de enquadramento compatível. Não integrar chave comercial ao frontend nem assumir que o projeto aberto autoriza todo uso do endpoint. [Termos](https://open-meteo.com/en/terms) e [planos](https://open-meteo.com/en/pricing).

MET Norway publica dados sob CC BY 4.0/NLOD salvo exceções, exige identificação, crédito e tráfego responsável, e não oferece SLA. Para Locationforecast global, o histórico não está disponível pela API: arquivar prospectivamente. [Termos](https://api.met.no/doc/TermsOfService), [licença](https://api.met.no/doc/License) e [modelo de dados](https://docs.api.met.no/doc/locationforecast/datamodel.html). Acesso sem chave não dispensa validação e controles HTTP.

## Identidade da previsão e antecedência

O serviço atual sem modelo fixado deve ser arquivado como **baseline operacional de seleção automática**, sem inventar modelo/rodada desconhecidos. Ele é um braço operacional separado, não uma origem meteorológica independente. O arquivo técnico novo exige identidade explícita e não aceita `auto`/`best_match` como modelo: a baseline automática precisará de envelope próprio que preserve essa incerteza antes da campanha.

Previous Runs usa deslocamento fixo em relação à validade; Single Runs seleciona a inicialização. Não tratar série contínua Historical Forecast nem ERA5 como cópia garantida da previsão conhecida na emissão. A escolha de produto, disponibilidade real e horário de coleta são parte do experimento. [Previous Runs](https://open-meteo.com/en/docs/previous-runs-api), [Historical Forecast](https://open-meteo.com/en/docs/historical-forecast-api), [Single Runs](https://open-meteo.com/en/docs/single-runs-api).

Registrar: provedor, modelo/versão, coordenadas, fuso IANA, rodada quando comprovada, emissão/disponibilidade quando informada, coleta UTC, validade início/fim, intervalo/amostragem, unidades e conteúdo original. Não usar generationtime_ms ou updated_at como inicialização de modelo sem documentação. Armazenar campo desconhecido como desconhecido.

## Sequência técnica da coleta

1. Preflight pontual nos locais propostos: campos, unidades, intervalos, horários, cobertura de D+1/D+3/D+7 e atribuições. Nenhuma campanha automática iniciada nesta revisão.
2. Acrescentar adaptadores experimentais, reaproveitando HTTP limitado, timeouts, limites de bytes e orçamento; não encaixar chamadas adicionais na requisição pública.
3. Arquivar JSON e proveniência sem sobrescrever. Implementado o primeiro componente em `climaprev.tools.experimental_archive`, ainda sem HTTP ou agendador.
4. Normalizar para instantes e intervalos UTC, preservando o fuso do dia civil e ausência de dados. A agregação da chuva precisa respeitar se o carimbo representa começo ou fim do intervalo. MET Norway não deve ter somas de 1/6/12 horas sobrepostas adicionadas juntas.
5. Separar observações, desenvolvimento, validação e teste; manifestos independentes para baseline automática e modelos explícitos.
6. Fechar desenho e fazer campanha prospectiva só após parâmetros e cronograma aprovados. Nenhuma adaptação do algoritmo operacional nesta etapa.

## Arquivo experimental implementado

`ForecastCapture` e `archive_forecast` preservam payload, origem/local, coleta, rodada opcional e intervalo [início,fim), além de hashes e antecedências reais. Nome por conteúdo separa modelo, provedor, rodada, local e alterações do payload. Escrita exclusiva impede sobrescrita e detecta corrupção de arquivo já existente. Limite por envelope: 4 MiB; JSON não finito é rejeitado.

Rodada desconhecida e coleta posterior ao começo do alvo recebem flags explícitas; nenhum arquivo é marcado como cientificamente aprovado. As datas declaradas ainda precisam ser comprovadas pelo adaptador. Os controles são necessários, não suficientes para elegibilidade confirmatória. O componente não valida campos meteorológicos, não normaliza intervalos, não coleta por HTTP e não é um cache operacional novo.

Não misturar esses arquivos com os snapshots históricos existentes nem com o cache operacional de consultas públicas. Sugestão para execução posterior: diretório ignorado `.historical-reports/prospective/`, mantendo só manifestos/resumos apropriados no Git.

## Validação desta entrega

Docker/Linux: 34 testes selecionados aprovados, cobrindo o arquivo novo e os planejadores anteriores (`test_experimental_archive`, `test_collect_campaign`, `test_spatial_plan`); mypy do módulo novo aprovado. Ruff dos dois arquivos novos aprovado. Os 18 testes específicos do arquivo também passaram no Windows; a execução ampliada Windows foi interrompida sem conclusão e não conta como aprovação. Tentativa inicial de Docker sem daemon foi superada após o usuário iniciá-lo. Não houve execução da suíte completa, chamada ao vivo dos novos modelos ou avaliação de precisão nesta entrega.

## Estimativa inicial de tráfego

Proposta de três estações, três modelos e uma rodada-alvo diária: nove capturas por dia se cada captura trouxer os três horizontes. MET Norway acrescentaria três, baseline operacional mais três: quinze requisições lógicas por dia, sem retries, consultas de observação e preflight. Sem batching, pode haver mais; peso de variáveis/modelos no faturamento deve ser verificado. Isso é estimativa de desenho, não consumo medido nem autorização de limites comerciais. Inicialmente concorrência um e sem retries automáticos de 429.
