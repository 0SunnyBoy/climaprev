# Preparação da referência observacional — 16/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Encerramento das pendências históricas — 20/10/2026

Importação real e comparação concluídas posteriormente para A201/A001/A801 de 2024. Reconciliação numérica de Belém e diagnóstico horário disponíveis; isso não é aceite científico. Próximas ações são revisão/critério de aprovação, sem nova calibração.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Entrega

Implementado o importador offline `climaprev.tools.inmet_observations`, com a convenção técnica [civil-day-preceding-hour-v1](convencao-observacional-v1.json). A implementação prepara a validação por estação; ainda não constitui validação científica nem comprova a equivalência entre estação e grade.

O importador aceita o layout CSV anual de estação automática, separado por ponto e vírgula, UTF-8 ou CP1252. Exige nome, código esperado, latitude, longitude, altitude e coluna de hora explicitamente UTC. Não deduz estação ou unidades pelo nome do arquivo. Cabeçalhos desconhecidos ou unidades diferentes das suportadas são rejeitados para revisão explícita.

Os campos aceitos são precipitação em mm, rajada em m/s e temperaturas máxima/mínima da hora anterior em °C. Rajadas são convertidas para km/h. Temperatura horária de bulbo seco não substitui extrema horária. Vazios e sentinela numérica -9999 viram ausência; outros valores não finitos ou chuva/rajada negativas são rejeitados. Extrema mínima superior à máxima também é rejeitada.

## Intervalos, cobertura e proveniência

Para cada dia local, são usados os endpoints posteriores à meia-noite inicial e até a meia-noite seguinte, inclusive. A contagem depende do tempo decorrido em UTC: dias de 23 e 25 horas são suportados. Cada variável exige 100% de cobertura; a falta de chuva não exclui uma rajada completa. Totais incompletos e extremos incompletos são nulos, com os horários ausentes listados.

O relatório conserva metadados do cabeçalho, hash dos bytes originais e hash do importador. O CLI limita a entrada a 32 MiB, não baixa arquivos e recusa sobrescrever evidência existente. O hash verifica consistência, não autenticidade da fonte nem qualidade do sensor. O CSV original deve ser preservado junto ao experimento.

Essa convenção segue a descrição de intervalos de precipitação, rajada e extremas no [glossário oficial do INMET](https://portal.inmet.gov.br/glossario/nublado). A diferença entre temperatura instantânea do modelo e extrema do sensor permanece uma questão de comparabilidade; não será resolvida aplicando automaticamente um deslocamento à temperatura.

## Execução quando houver arquivo oficial

O exemplo abaixo usa um caminho de destino proposto para o CSV; esse arquivo **ainda não foi obtido**. Confirmar a identidade e os metadados de A201 no cabeçalho e no catálogo antes de interpretar resultados.

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m climaprev.tools.inmet_observations --input .historical-reports/inmet/A201-2025.csv --station A201 --timezone America/Belem --start 2025-01-01 --end 2025-01-31 --output .historical-reports/inmet/A201-2025-01-observations-v1.json
```

Para completar 31/01 em Belém, a entrada precisa conter também os endpoints até 01/02 às 03h UTC. Não é necessário acessar outro ano para esse recorte; na virada do ano pode ser necessário o arquivo seguinte.

## Estado do acesso oficial

O [portal de históricos anuais do INMET](https://portal.inmet.gov.br/dadoshistoricos) continua indicando o arquivo de 2025. A busca complementar não forneceu uma série bruta alternativa oficial validada para A201. A falha de conexão documentada na auditoria anterior permanece sem resolução. Não foram usados espelhos de terceiros, estimativas do gráfico ou dados sintéticos como observação real.

Os testes utilizam fixtures sintéticas do formato CSV; ainda falta teste de compatibilidade com um arquivo oficial real. Nenhum resultado de chuva ou temperatura INMET foi calculado nesta etapa.

## Verificação e próximas ações

Os testes cobrem identidade, unidades, vírgula decimal, encodings, sentinelas, duplicatas, ausência na fronteira, DST, extremas e preservação da evidência. Os resultados finais da regressão portátil são registrados em [evidence/importacao-inmet-2026-10-16.json](evidence/importacao-inmet-2026-10-16.json).

Próxima ordem: obter e validar CSV real → alinhar fronteiras GFS/ERA5 → gerar casos pareados com a estação → ampliar sazonalidade e eventos → congelar protocolo científico → ajustar A/B. A reference-v1 e os snapshots originais permanecem preservados; não houve promoção, commit ou push.
