# reference-candidate-1 — protocolo do piloto diagnóstico

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Data: 16/10/2026, America/Sao_Paulo. Estado: proposta de diagnóstico técnico;
desenho científico e promoção pendentes. O início do trabalho autoriza preparar
ferramentas e verificar a baseline, sem aprovar limiares ou coeficientes novos.

## Objetivo e limites

Verificar coleta, qualidade, rastreabilidade, reprodução offline e comparação
pareada, e produzir um diagnóstico inicial de erros da `reference-v1`. As
regras ativas da aplicação e o perfil `disabled` permanecem a baseline.

O alvo inicial é `reference-v1-on-reanalysis`: classificações da v1 sobre a
reanálise ERA5, congeladas e compartilhadas entre variantes. Não são rótulos
independentes de impacto, nem validação da correção dos limiares da v1.
Concordância com esse alvo deve ser descrita como concordância heurística.
Erros dos valores meteorológicos também são relativos à reanálise, que tem
suas próprias limitações de resolução e representação local.

## Escopo inicial proposto

| Item | Definição do piloto |
| --- | --- |
| Localidade | Belém, PA; latitude -1.4558, longitude -48.5044 |
| Fuso | `America/Belem` |
| Previsão arquivada | Previous Runs, modelo explícito `gfs_global` |
| Referência meteorológica | Historical Weather, modelo explícito `era5` |
| Antecedências | 1, 3 e 7 dias |
| Janela de exemplo | 01–31/01/2025; pequenas janelas adicionais de 2025 somente para diagnóstico |
| Cobertura | 100% das horas esperadas de cada variável que sustenta o evento, nos dois conjuntos |
| Eventos | Chuva horária, chuva diária, rajada, calor e frio |
| Unidades | °C, mm e km/h; chuva horária derivada dos intervalos horários |
| Partição executada | `diagnostic` |

A disponibilidade real do arquivo do modelo e de cada variável deve ser
verificada. Não substituir silenciosamente o modelo quando faltar cobertura.
Frio pode não ter suporte no piloto de Belém; isso deve aparecer nas contagens
e métricas, sem simular casos positivos ou ampliar alegações a outras regiões.

Ausências não viram zero. A elegibilidade é independente por evento; o risco
geral só usa dias elegíveis em todos os eventos. Umidade e código meteorológico
são solicitados/normalizados, mas não sustentam a elegibilidade desses cinco
eventos. O relatório deve registrar exclusões e horas válidas/esperadas, além
dos acertos. Denominador zero produz `null` na métrica experimental aplicável;
`null` não significa desempenho perfeito.

## Sequência de execução

1. Registrar revisão do código e ambiente, modelos, fuso e janela escolhida.
2. Coletar cada combinação janela/antecedência com `validate_historical`,
   `--minimum-coverage 1.0` e `--save-input`, usando arquivos separados.
3. Auditar payloads/unidades, horas e exclusões. Falha de coleta ou cobertura
   insuficiente é um resultado diagnóstico a registrar.
4. Reexecutar com `validate_historical --input` sem rede e verificar que as
   classificações, contagens e métricas são reproduzidas.
5. Agregar snapshots com `compare_historical --input ... --protocol ...
   --partition diagnostic --output ...`, inicialmente apenas R0.
6. Descrever erros e lacunas, sem escolher ajustes a partir de um teste final.
7. Definir protocolo científico, amostra, alvos e critérios com revisão; depois
   decidir qual experimento A/B merece ajuste primeiro.

Os comandos completos estão em [validação e calibração](../../arquitetura/validacao-e-calibracao.md).
Nenhuma execução ou resultado numérico é presumido neste protocolo. Artefatos
gerados posteriormente precisam registrar suas próprias evidências.

## Dois experimentos e combinação posterior

| Variante | Valores | Regras | Pergunta |
| --- | --- | --- | --- |
| R0 | Originais | V1 | Qual é o desempenho de partida? |
| A | Originais | Candidata | Alterar regras melhora a classificação? |
| B | Calibrados | V1 | Corrigir valores reduz erros meteorológicos e omissões? |
| AB | Calibrados | Candidata | A combinação agrega ganho sem regressões inaceitáveis? |

O comparador prepara essas variantes quando os arquivos `--candidate` e/ou
`--calibration` são fornecidos. Ainda não há limiares ou coeficientes aprovados
para este piloto. Todas as variantes usam os mesmos casos elegíveis e o mesmo
alvo congelado. MAE/RMSE melhores não garantem classificação melhor; classificar
melhor não comprova melhora dos valores previstos.

## Divisão temporal ilustrativa, sem teste reservado declarado

O [JSON do protocolo](protocolo-piloto.json) traz apenas um exemplo de formato:

| Partição futura proposta | Período ilustrativo |
| --- | --- |
| `adjustment` | 2024 |
| `validation` | Janeiro–junho de 2025 |
| `test` | Julho–dezembro de 2025 |

Esses splits não estão aprovados. A cobertura do arquivo de previsão de 2024,
a representatividade e a suficiência da amostra ainda precisam ser verificadas.
Datas, episódios e antecedências exigem desenho contra vazamento temporal;
intervalos cronológicos disjuntos no arquivo não resolvem sozinhos essa questão.

O piloto usa `diagnostic`, mesmo quando uma janela cai dentro dos intervalos
ilustrativos. Se resultados de uma janela forem vistos para orientar decisões,
essa janela não poderá ser declarada depois como teste final intocado. A seleção
do conjunto reservado será formalizada antes do ajuste e da avaliação final.

O CLI valida ordem e ausência de sobreposição dos splits, e usa o intervalo
selecionado para filtrar datas. Os demais campos do JSON registram intenções:
não são controles de aprovação executados pelo programa. `--partition test`
não autoriza promoção, e todos os relatórios permanecem diagnósticos nesta etapa.

## Artefatos e rastreabilidade

Guardar snapshots brutos, configuração, consultas, coleta, revisão do código,
hashes dos algoritmos, relatórios e exclusões. Unidades horárias explícitas
são verificadas. O replay rejeita algoritmos distintos dos registrados;
mudanças no pipeline exigem migração explícita do dataset.
SHA-256 identifica o conteúdo e detecta divergência
em relação ao hash registrado; não autentica o provedor nem impede alteração
acompanhada de recálculo. Preservar a procedência exige também revisão e
custódia dos artefatos. Não sobrescrever snapshots diferentes; usar nova
identidade de arquivo para nova coleta.

O relatório permite matriz de confusão, precisão/recall/F1, detecção de
`moderate`/`high`, viés, MAE e RMSE por evento, antecedência, localidade e mês.
Estratos mensais descrevem a amostra; não são estações regionais validadas.
Incerteza e tamanho suficiente da amostra permanecem trabalho científico
pendente. A decisão produzida é `diagnostic_only_not_approved`.

## Decisões ainda necessárias

- Fonte/definição dos rótulos independentes que sustentariam alegações de impacto.
- Escopo geográfico, sazonal e de eventos do estudo representativo.
- Splits definitivos, cobertura do arquivo e separação de episódios/antecedências.
- Metas numéricas, tolerâncias a regressão e suficiência amostral por estrato.
- Revisor especializado, procedimento de revisão e critérios de promoção.
- Regras da candidata e coeficientes, somente após diagnóstico e com justificativa.

Nenhuma promoção é automática. Manter a v1, ampliar o estudo ou rejeitar uma
candidata são resultados possíveis; ausência de evidência não é aprovação.
