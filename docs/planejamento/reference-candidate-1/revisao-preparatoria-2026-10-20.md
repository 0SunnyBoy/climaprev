# Revisão preparatória das fontes e reservas — 20/10/2026

Estado: revisão técnica consolidada para aceite do responsável pelo projeto. O usuário confirmou nesta conversa que fará o aceite final. Isso identifica responsabilidade, mas não constitui aprovação dos critérios, das fontes ou da candidata. Reference-v1 ativa; nenhuma calibração, promoção ou nova leitura dos outcomes reservados neste lote.

## Parecer técnico por questão

| Questão | Constatação | Encaminhamento |
|---|---|---|
| Fonte observada | CSVs oficiais de 2024 de A201/A001/A801 possuem origem/hash e comparação registradas | Preservar arquivos, qualidade e exclusões; estação não representa todo o município |
| Chuva | Reconciliação numérica do boletim de Belém concluída com dia encerrado às 12 UTC; produto usa dia civil local | Manter dois alvos separados e fronteira mensal; reconciliação não aprova intercambialidade |
| Extremos térmicos | Extremos de intervalo INMET versus amostras horárias instantâneas do modelo | Comparação descritiva até validar equivalência; não usar a diferença como viés automaticamente corrigível |
| Rajada | Amostragem/intervalos diferem, inclusive rajada ERA5 instantânea | Aprovar convenção antes de inferência; controle ERA5 não substitui estação |
| Espaço | Consulta municipal/estação pareada; resultados mistos e altos não recuperados | Manter ambos, sem escolher braço mais favorável para produção |
| Eventos raros | Altos se concentram em seis unidades local/data; calor/frio sem altos | D+1/D+3/D+7 não triplicam amostra independente; recall sem eventos permanece indefinido |
| Incerteza | Janeiro tem segmento de três dias, inferior ao bloco primário sete; bootstrap técnico disponível | Não excluir janeiro retroativamente nem apresentar intervalo inválido; eventual novo desenho deve ser prospectivo |
| Reservas | Inventário local sem correspondência conhecida dos períodos jul–dez/2025 e jan–jun/2026; CSV anual 2025 foi processado estruturalmente | Independência não demonstrada. Não certificar ausência de acesso anterior, remoto ou em outra máquina |
| Ganho | Nenhum experimento demonstra candidata substancialmente superior à v1 | Ganho de ferramentas não é ganho de previsão; evolução permanece para o final |

## Decisão recomendada para deliberação

Tratar 2024 como diagnóstico exploratório já conhecido, não validação inédita. Manter reservas antigas como **independência não comprovada**, sem promovê-las a teste confirmatório até decisão explícita de proveniência. Se a independência não puder ser demonstrada, planejar nova avaliação prospectiva sem escolher períodos por desempenho ou abrir outcomes para decidir sua inclusão. Nenhuma coleta/partição nova foi executada aqui.

A definição de responsável resolveu essa lacuna administrativa. Permanecem para o aceite do usuário: adequação por variável, proveniência, objetivos primários, margem de ganho e tolerâncias. Não atribuir ao usuário uma qualificação científica não declarada; revisão especializada continua recomendável para semântica instrumental.

## Fontes e evidências

A documentação da [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) descreve reanálise, agregações horárias e amostragem; não a apresenta como observação instrumental de impacto. A [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) distingue arquivo de previsões e execuções/modelos. As [diretrizes WMO de verificação](https://public.wmo.int/media/news/wmo-issues-guidelines-verification-of-hydrological-forecasts) reforçam objetivos definidos e comparação com observações; não aprovam os limiares particulares deste projeto.

Evidências locais: [diagnóstico horário e inventário](diagnostico-horario-e-reservas-2026-10-19.md), [diagnóstico consolidado](diagnostico-e-adendo-2026-10-19.md), [experimento espacial](experimento-espacial-2026-10-19.md). Esta revisão leu relatórios existentes; não abriu novos valores reservados.
