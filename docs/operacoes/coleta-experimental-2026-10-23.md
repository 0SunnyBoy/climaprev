# Coleta experimental e preflight de fontes

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Data: 23/10/2026. Implementação local posterior à base publicada `5a6fc9c`, sem commit/push. Reference-v1, rotas públicas, janela de sete dias e infraestrutura operacional preservadas. Não houve fitting, acesso a novos outcomes reservados ou avaliação de precisão.

## Entregas

- `tools/experimental_collection.py`: execução pontual sequencial para GFS, IFS025, ICON global e MET Norway; seleção por CLI, sem retries, redirects ou uso de proxy implícito do ambiente. Usa o cliente HTTP limitado existente, timeout e limite de 4 MiB por resposta. Identificação da aplicação e Accept JSON enviados. Não agenda nem adiciona chamadas ao endpoint público.
- `tools/experimental_normalization.py`: medições com unidade, timestamp UTC, intervalo e semântica explícitos. Temperatura, umidade e vento; chuva e rajada horária Open-Meteo. Vento MET em m/s convertido para km/h. Rajada MET não é convertida silenciosamente em máximo horário, pois a equivalência ainda precisa ser resolvida.
- Chuva Open-Meteo atribuída à hora anterior ao timestamp; MET aos intervalos seguintes de 1/6/12 horas. No MET, escolha do menor período disponível sem sobreposição. Não somar simultaneamente next_1_hours e next_6_hours do mesmo trecho.
- Soma de chuva só quando os intervalos cobrem exatamente o dia solicitado. Lacunas, nulos, sobreposições e acumulados que atravessam a fronteira do dia resultam em `null`; sem divisão uniforme de acumulados de seis horas nem substituição por zero.
- Arquivo bruto preserva parâmetros enviados e resposta do fornecedor, junto da proveniência já implementada. Resultados normalizados saem em JSON por linha; payload inválido rejeitado antes do arquivo normal. O diagnóstico bruto da rejeição ficou separado em diretório ignorado.

## Preflight ao vivo

Executado no Docker em coordenadas municipais de Belém, Brasília e Porto Alegre, não em coordenadas instrumentais certificadas. Doze combinações local/fonte; onze aceitas pela normalização, uma rejeitada. [Resumo versionado](evidence/preflight-experimental-2026-10-23.json). JSONs completos ficaram em `.report-work/`, fora do Git.

| Fonte | Resultado na amostra | Restrição |
|---|---|---|
| GFS global | Aceito nos três locais; chuva diária completa em D+1/D+3/D+7 após ajuste da fronteira | Nenhuma inicialização de rodada comprovada no payload |
| IFS025 | Belém e Brasília aceitos e completos; Porto Alegre rejeitado | Captura de Porto Alegre continha −0,1 mm em três horários; não corrigido para zero |
| ICON global | Aceito nos três locais, D+1/D+3 completos; D+7 incompleto | Não extrapolar limite do modelo para completar o dia |
| MET Norway | Aceito nos três locais, D+1 completo; D+3/D+7 sem soma diária elegível | Acumulados de seis horas atravessam a fronteira do dia local; não significa inexistência de previsão |

O primeiro preflight local via urllib falhou no certificado do MET Norway; no Docker, TLS permaneceu ativo e a coleta funcionou. Isso identifica diferença de ambiente, não prova causa interna do certificado nem indisponibilidade da fonte.

Uma tentativa inicial de oito datas UTC não cobria a madrugada final de D+7 no fuso brasileiro. O coletor passou a solicitar nove datas experimentais para GFS/IFS e manteve oito para ICON; regressão simula o provedor respeitando o tamanho pedido. Isso **não amplia a janela pública**. Falhas da primeira tentativa não foram usadas como evidência de cobertura final.

Os rótulos D+1/D+3/D+7 destes relatórios são dias civis após a **coleta**. Não são antecedências verificadas a partir da inicialização. `run_at=null` permanece explícito; `generationtime_ms` e atualização do feed MET não foram tratados como rodada. O arquivo integral também contém trechos anteriores à coleta, sinalizados pelo envelope; a elegibilidade de um alvo futuro exige verificação própria.

## Execução pontual

Com a imagem de desenvolvimento atualizada e permissões de escrita na pasta montada:

```powershell
docker compose run --rm --no-deps app python -m climaprev.tools.experimental_collection --latitude -1.4558 --longitude -48.5044 --timezone America/Belem --output /app/.historical-reports/prospective --models gfs_global ecmwf_ifs025 icon_global met-norway
```

Persistir a pasta de saída por bind mount conforme o runbook antes de uma campanha; sem montagem, o `--rm` remove os arquivos do contêiner. Durante o preflight foi usada montagem explícita de `.report-work`. O CLI usa saída JSON por fonte e exit code 1 se qualquer fonte falhar, preservando os resultados das demais. Não iniciar rotina recorrente com este comando: ainda falta orçamento compartilhado de campanha/agendamento, configuração congelada e baseline operacional arquivada. Não há serviços empresariais ou API comercial novos nesta entrega.

## Validação

57 testes selecionados Docker/Linux aprovados, incluindo arquivo, coletores, normalização e planejadores anteriores. Mypy aprovado nos três módulos novos; Ruff aprovado no host Windows nos módulos/testes novos. Primeira rodada do Ruff em bind mount Linux recebeu EXE002 de permissão de arquivos Windows e um erro de tipo; erro de tipo corrigido, checagem do host passou sem desativar regra no projeto. Sem execução integral da suíte neste incremento e sem CI remoto do diff local.

## Próximos trabalhos

1. Identidade de rodada/disponibilidade e captura da baseline automática com origem desconhecida preservada.
2. Manifesto de campanha, deduplicação entre provedores/modelos e orçamento compartilhado; agendamento só após parâmetros e calendário aprovados.
3. Normalização observacional pareada por estação/intervalo, relatório de qualidade e decisão explícita para entradas inválidas como a chuva negativa; nunca ajustar regras após observar qual braço fica melhor.
4. Finalizar aceites da campanha antes do teste confirmatório. Leitor de tela ainda pendente. Sem superioridade comprovada da candidata.

Referências de semântica: [Open-Meteo](https://open-meteo.com/en/docs), [schema oficial de modelos](https://github.com/open-meteo/open-meteo/blob/main/openapi/forecast.yml), [formato MET](https://docs.api.met.no/doc/ForecastJSON.html), [modelo de dados MET](https://docs.api.met.no/doc/locationforecast/datamodel.html). Consultadas nesta continuação; não aprovam os critérios quantitativos do projeto.
