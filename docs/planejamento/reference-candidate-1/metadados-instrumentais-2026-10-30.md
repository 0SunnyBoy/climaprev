# Metadados instrumentais — revisão de 30/10/2026

> **Atualização de implementação:** [infraestrutura D+7 e refatoração](../../operacoes/refatoracao-controle-d7-2026-10-30.md) implementadas após esta especificação/revisão; execução desativada. O texto original abaixo preserva o estado preparatório, inclusive o coletor ainda não implementado naquele checkpoint. Altura, calibração e representatividade individuais continuam sem comprovação.

## Resultado

Revisão documental concluída até o limite das evidências disponíveis. Identidade das três estações e contratos temporais catalogados; **equivalência instrumental integral ainda não comprovada**. Não liberar variáveis incompatíveis por ausência de metadados. Esta revisão não altera importadores, protocolo v5, calendário ou hashes do piloto.

## Identidade e proveniência

| Código | Estação | Latitude / longitude do catálogo usado | Altitude da estação (m) | Identificador OSCAR declarado pelo catálogo |
|---|---|---|---|---|
| A201 | Belém | -1.41111111 / -48.43944444 | 21.17 | 0-2000-0-81680 |
| A001 | Brasília | -15.78944444 / -47.92583332 | 1160.96 | 0-2000-0-86715 |
| A801 | Porto Alegre — Jardim Botânico | -30.05361111 / -51.17472221 | 41.18 | 0-2000-0-86988 |

Origem: catálogo oficial arquivado na preparação de 30/10 e ligado por hash aos CSVs TEMPO. Os registros selecionados e hashes são preservados no [inventário](metadados-instrumentais-2026-10-30.json). A consulta web ao [catálogo oficial](https://apitempo.inmet.gov.br/estacoes/T) foi possível nesta revisão; a nova obtenção integral pelo terminal falhou, portanto **não há novo snapshot bruto autenticado nesta rodada**. O inventário mantém explicitamente a origem do snapshot anterior.

Altitude não é altura de sensor. O identificador OSCAR permite investigação, mas não certifica sozinho instrumento ou calibração. A página OSCAR consultada não expôs ficha instrumental utilizável no extrator. Não preencher campos ausentes com convenções de rede.

A801 é Jardim Botânico: o INMET distingue essa estação de Belém Novo em sua [notícia oficial sobre Porto Alegre](https://portal.inmet.gov.br/noticias/porto-alegre-rs-ganha-nova-esta%C3%A7%C3%A3o-meteorol%C3%B3gica-autom%C3%A1tica). Não substituir estações pelo nome da cidade.

## Contratos e decisões

| Variável | INMET: contrato documentado | Previsão Open-Meteo | Decisão |
|---|---|---|---|
| Temperatura horária | Média da hora anterior | Instantânea, 2 m | Incompatível; não fabricar média a partir de instantâneos |
| Temperatura máxima/mínima horária | Extremos da hora anterior | Série horária instantânea não representa esses extremos | Preservar extremos observados; exigir previsão nativa equivalente |
| Umidade horária | Hora anterior, agregação insuficientemente explícita | Instantânea, 2 m | Bloqueada para pareamento instantâneo |
| Velocidade do vento | Média dos dez minutos anteriores | Instantânea, 10 m | Incompatível; altura igual não resolve agregação diferente |
| Rajada | Máxima da hora anterior | Máxima da hora anterior, 10 m | Compatibilidade temporal possível; altura observada e representatividade pendentes |
| Precipitação | Acumulação observada, importada com intervalo explícito | Soma da hora anterior | Alvo primário exploratório sob cobertura e intervalos completos; procedência e representatividade continuam limitantes |

Contratos consultados no [glossário INMET](https://portal.inmet.gov.br/glossario/nublado) e nas [definições horárias Open-Meteo](https://open-meteo.com/en/docs). Conversão de m/s para km/h usa fator 3,6; não muda a semântica da medida. Os contratos do MET Norway exigem revisão própria; não herdam automaticamente as definições Open-Meteo.

O exportador TEMPO chama campos de `Temp. Ins.` e `Umi. Ins.`. O rótulo não supera a divergência ou ambiguidade documental: `convert_tempo_csv` mantém temperatura instantânea excluída e não transforma umidade em observação instantânea certificada.

## Lacunas por estação

Para **cada uma de A201, A001 e A801**, continuam sem comprovação individual nas fontes examinadas: altura acima do solo por sensor, fabricante/modelo/número de série, calibração e validade, histórico de troca/manutenção, exposição e obstáculos, mudanças de local, classificação de representatividade e semântica exata do campo de umidade exportado. Operante não significa qualidade validada.

O [INMET informa que os dados automáticos são brutos](https://portal.inmet.gov.br/noticias/saiba-como-acessar-os-dados-meteorol%25C3%25B3gicos-dispon%25C3%25ADveis-no-site-do-inmet). Valores ausentes permanecem ausentes; qualidade de transmissão e completude não substituem consistência meteorológica ou rastreabilidade metrológica.

## Como encerrar as lacunas

Obter ficha oficial válida para o período de cada série, contendo código/WSI, sensor, altura, agregação, calibração e histórico. Registrar URL ou documento original, data real de obtenção, hash e período de validade. Revisar a relação entre ponto solicitado, célula de grade retornada, altitude e exposição local. Só então atualizar a declaração instrumental e avaliar a elegibilidade por variável. Se for necessário contato institucional, preparar a solicitação e obter autorização antes de enviá-la.

Essas lacunas não impedem a coleta do piloto primário de chuva já autorizada; impedem declarar equivalência completa e promover análises secundárias a confirmação. [Desenho D+7](controle-d7-prospectivo-2026-10-30.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).
