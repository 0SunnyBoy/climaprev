# Experimento espacial — preparação em 19/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Estado atualizado: coletor implementado, preflight real aprovado, 72 snapshots coletados sem falhas e 180 estratos comparados. A reference-v1 continua ativa, sem ajuste ou promoção. O planejamento abaixo preserva o desenho anterior aos resultados.

## Desenho congelado

O arquivo `evidence/plano-espacial-2024-2026-10-19.json` descreve 72 snapshots (144 chamadas sem contar retries): controle municipal novo e braço nas coordenadas da estação, para Belém, Brasília e Porto Alegre, janeiro/abril/julho/outubro de 2024, D+1/D+3/D+7. Avaliam-se dias 1–28; dia 29 fornece apenas a fronteira horária.

Coordenadas e altitude vêm dos cabeçalhos dos CSVs anuais de 2024, conferidos contra os hashes dos registros de obtenção oficiais:

| Estação | Latitude | Longitude | Altitude (m) |
|---|---:|---:|---:|
| A201 | -1.411228 | -48.439512 | 21.17 |
| A001 | -15.78944444 | -47.92583332 | 1160.96 |
| A801 | -30.05361111 | -51.17472221 | 41.18 |

Cada par mantém altitude da estação, `cell_selection=nearest`, modelos, unidades, fuso, período e horizonte idênticos. Apenas latitude/longitude variam. A seleção de célula e a altitude influenciam a consulta segundo a [documentação oficial Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api). O preflight precisa verificar o suporte dos parâmetros nos dois endpoints antes da coleta completa; não se admite fallback silencioso.

O controle municipal deve ser coletado novamente no mesmo lote. A coleta antiga usou os padrões do provedor para altitude/seleção e pode ter ocorrido antes de revisões do arquivo meteorológico: permanece referência histórica, mas não constitui o braço pareado deste experimento. A coordenada retornada representa a célula da grade; proximidade da consulta não garante melhoria de previsão ou resolução de extremos locais.

## Sequência planejada e executada

1. Implementar coletor isolado com preflight, limites de concorrência/retries e registro de falhas, horários, coordenadas e altitude retornadas; preservar snapshots anteriores.
2. Coletar os dois braços e verificar completude, identidade dos parâmetros e hashes.
3. Comparar somente a interseção dos dias elegíveis originais e dos dois braços por variável. Manter os cinco eventos, estratos e limitações de bootstrap existentes.
4. Registrar diferenças de erro/detecção sem escolher limiares, ajustar coeficientes ou promover candidata. Melhora agregada isolada não representa aceite científico.

## Reprodução e verificação

Com `PYTHONPATH=src`, executar `python docs/planejamento/reference-candidate-1/scripts/prepare_spatial_2024.py`. O script recusa substituir plano divergente. Testes novos verificam igualdade dos controles, identidade/hash/ano dos CSVs e bloqueio de mudança de escopo ou fitting. Não se alteraram configuração do coletor anterior nem arquivos usados no fingerprint dos algoritmos históricos.

Verificação concluída: 42 testes direcionados aprovados, incluindo os sete novos; Ruff e mypy aprovados. O registro operacional distingue as tentativas afetadas pelo ambiente da repetição aprovada.

## Resultados da coleta e comparação

Evidências: `evidence/preflight-espacial-2026-10-19.json`, `evidence/coleta-espacial-2026-10-19.json` e `evidence/comparacao-espacial-2024-2026-10-19.json`. Os 72 snapshots imutáveis estão em `.historical-reports/spatial-2024-2026-10-19/`, com hashes no manifesto. O preflight foi reutilizado, evitando quatro chamadas repetidas. O plano congelado continua declarando seu estado anterior à execução; o manifesto registra a execução efetiva.

O coletor valida altitude retornada (tolerância 0,1 m), coordenadas finitas, fuso, estrutura/unidades e séries horárias, com timeouts/retries limitados pelo cliente HTTP existente. Falha no primeiro par impede expansão; snapshots completos podem ser retomados somente com configuração e requisições idênticas. `nearest` é enviado explicitamente, mas o provedor não devolve esse parâmetro: não se afirma verificação independente da implementação interna da seleção.

Não houve exclusão adicional da elegibilidade anterior: por horizonte, 252 unidades local/data de chuva diária e horária, 249 de rajada e 248 de cada extremo térmico. As 180 comparações geraram 30 agregações (cinco eventos × três horizontes × dois braços). Os horizontes compartilham observações e não multiplicam a amostra independente.

MAE GFS em D+1, controle municipal → consulta na estação:

| Variável | Controle | Estação | Unidade |
|---|---:|---:|---|
| Chuva diária | 5,384 | 5,244 | mm/dia |
| Máxima horária de chuva | 2,347 | 2,288 | mm |
| Rajada | 7,247 | 7,247 | km/h |
| Temperatura máxima | 1,629 | 1,591 | °C |
| Temperatura mínima | 1,525 | 1,771 | °C |

O ganho não é uniforme: chuva diária/horária e temperatura máxima têm MAE maior no braço da estação em D+3; temperatura mínima piora nos três horizontes. Rajada mantém os mesmos resultados. Nenhum braço detectou os altos observados de chuva horária (2), diária (4) ou rajada (3), em qualquer horizonte. Em chuva diária D+3, falsos alarmes altos aumentaram de 1 para 2 no braço da estação.

Os centros retornados coincidem entre braços em 24/36 pares GFS e 36/36 ERA5. A identidade dessas coordenadas não garante identidade de toda a série ou ausência de interpolação; não foi investigado o mecanismo interno do provedor. A representação espacial isolada não resolveu a falta de detecção nesta amostra. A comparação é descritiva, sem intervalo inferencial aprovado, sem alteração de limiares e sem aprovação de candidata.

## Encaminhamento atualizado em 20/10/2026

O catálogo e o diagnóstico horário abaixo propostos já foram concluídos: 3.747 casos e 37 registros altos relevantes, com inventário local das reservas. Consulte [diagnóstico vigente](diagnostico-horario-e-reservas-2026-10-19.md). Restam revisão científica, proveniência/independência, suporte e critérios prospectivos. A evolução da candidata foi deixada por último; os resultados descritivos deste documento não mudaram.

## Sequência proposta originalmente — preservada como histórico

1. Catalogar os casos de alto risco perdidos e falsos alarmes por evento/local/data, mostrando os valores dos dois braços e a semântica de cada variável.
2. Consolidar os limites de resolução, amostragem e suporte de eventos raros antes de propor novos dados ou alterar critérios.
3. Resolver critérios de aceite e revisão científica para encerrar a preparação. Ajuste e promoção continuam fora da autorização atual.

Verificação final deste incremento: 79 testes direcionados aprovados, Ruff aprovado e mypy aprovado nos três módulos espaciais. A suíte completa anterior de 574 testes não foi repetida. O PDF acadêmico permanece inalterado.
