# Revisão das implementações após obtenção do CSV oficial

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Encerramento das pendências históricas — 20/10/2026

A revisão com CSV avançou para as três estações de 2024, cinco eventos, comparação espacial e diagnóstico horário. Pendências antigas de importação, coleta espacial e catálogo foram superadas tecnicamente; revisão científica e independência das reservas não foram aprovadas.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 16/10/2026. Escopo: revisar etapas 1 a 5 com observações INMET disponíveis, preservando a parada antes da etapa 6.

## Estado atualizado

O impedimento de acesso ao CSV foi resolvido. O arquivo oficial A201/Belém de 2025 foi obtido e aceito pelo importador, e as comparações reais de janeiro foram executadas nos três horizontes. As antigas pendências de “obter CSV”, “validar o formato real” e “executar comparação observacional no piloto” podem ser encerradas tecnicamente. Isso não encerra a revisão científica da fonte nem conclui a preparação de uma base representativa para ajuste.

| Etapa | Concluído agora | O que permanece |
|---|---|---|
| 1. Importação INMET | Obtenção oficial, CRC/hash, identidade/cabeçalho, encoding e processamento real de A201. | Revisar a qualidade da série e reconciliar a diferença com o boletim. Validar outras estações quando incorporadas. |
| 2. Comparação de chuva | Estação × GFS × ERA5, D+1/D+3/D+7, 31 dias completos em janeiro/2025. | Revisar representatividade espacial e expandir a comparação observacional. |
| 3. Temperatura e rajada | Comparadores implementados e executados com CSV real nos três horizontes; diferenças temporais registradas. | Aprovar a adequação científica entre amostras instantâneas e extremos de intervalo. `calibration_ready` continua falso. |
| 4. Ampliação histórica | Coleta 2024 em Belém, Brasília e Porto Alegre: 36 snapshots, 261 unidades local/data pareadas. | Essa expansão continua usando ERA5; ainda falta observação INMET correspondente aos locais/janelas ampliados e suporte suficiente de eventos severos. |
| 5. Congelamento | Desenho técnico, campanha e código preservados; CSV e resultados reais acrescentados por manifesto suplementar. | Congelar alvos observacionais de risco, completar a auditoria de reserva e aprovar métrica principal, suficiência, ganho mínimo e revisão científica. |
| 6. Ajuste de classificação | **Não iniciado.** | Fora da autorização atual. |

“Concluído” nesta tabela significa entrega técnica no escopo do piloto, não aprovação da futura reference-candidate-1 para produção.

## Evidências verificadas nesta revisão

O CSV contém 8.760 registros horários. Identidade e posição no cabeçalho coincidem com o catálogo oficial: A201, BELEM, latitude -1,41111111, longitude -48,43944444 e altitude 21,17 m. Janeiro tem 31 dias completos para as variáveis comparadas.

Foi criado [congelamento-suplementar-estacao-a201.json](../planejamento/reference-candidate-1/evidence/congelamento-suplementar-estacao-a201.json), que:

- Confere o hash do CSV contra a evidência de validação real.
- Confere os hashes dos seis relatórios de comparação, dois por horizonte.
- Confirma que todos os relatórios usam o mesmo CSV.
- Verifica a preservação dos 36 pais da campanha 2024 e dos 56 arquivos de origem congelados anteriormente.
- Acrescenta nove arquivos de evidência, preservando o manifesto anterior.
- Mantém aprovação científica falsa e etapa 6 sem iniciar.

O resumo dos resultados é [validacao-estacao-real-a201.json](../planejamento/reference-candidate-1/evidence/validacao-estacao-real-a201.json). O [relatório de acesso](RELATORIO-ACESSO-INMET-2026-10-16.md) contém a proveniência da obtenção e o teste controlado do User-Agent.

## Pendências que precisam ser concluídas antes de ajustar a candidata

### 1. Reconciliar a referência de chuva

CSV: 427,6 mm no janeiro civil e 427,0 mm pelo agrupamento UTC dos timestamps. Boletim: 417,0 mm. A diferença não se explica somente por essas duas convenções. É preciso esclarecer a versão/qualidade/cálculo da fonte antes de tratar o total como referência científica aprovada. Não corrigir o CSV artificialmente para coincidir com o boletim.

### 2. Revisar a localização e a semântica das variáveis

As grades atuais ficam a 10,333 km da estação no GFS e 11,958 km no ERA5. O experimento usa o ponto municipal original, preservado para permitir comparação histórica. Uma coleta complementar nas coordenadas da estação pode ajudar a separar efeitos de localização; ela deve constituir experimento identificado, sem sobrescrever o original.

Temperatura instantânea e extrema da hora anterior não são medições idênticas. A documentação também distingue a rajada GFS da rajada ERA5. Os comparadores informam essas diferenças; seus erros ainda não devem virar coeficientes automaticamente.

### 3. Completar a expansão com observações de estação

A expansão 2024 está coletada para modelos/reanálise, mas a observação real analisada até agora é apenas A201 em janeiro/2025. Obter séries oficiais correspondentes de 2024, confirmar estações representativas dos três locais e executar os mesmos cruzamentos nas janelas predefinidas.

Reavaliar cobertura e suporte sobre observações reais. Na expansão ERA5 houve apenas dois dias de chuva diária alta e nenhum evento alto nos demais tipos; isso não demonstra suficiência para otimizar detecção de alto risco.

### 4. Preparar e congelar os alvos observacionais de risco

Os novos cruzamentos com estação calculam erros meteorológicos. Eles ainda não constituem uma avaliação de classificação de risco contra alvos observacionais congelados.

Antes da etapa 6, identificar e versionar os rótulos por evento derivados da observação validada, aplicando somente os limiares atuais da reference-v1. Registrar qualidade, exclusões, fonte e convenção; preservar a distinção dos rótulos anteriores de reanálise. Preparar esses alvos não exige ajustar limiares, mas a adequação científica da referência deve ser resolvida primeiro.

### 5. Fechar o protocolo científico e sua reserva

O desenho técnico está congelado, mas continuam pendentes revisor, evento/métrica principal, suporte mínimo, precisão esperada, ganho relevante e tradeoffs de falsos alarmes. O plano de bootstrap está especificado, não implementado ou executado.

O CSV anual 2025 contém observações de julho–dezembro, período reservado documentalmente para validação. Foi obtido e processado estruturalmente, mas só janeiro teve métricas agregadas/examinadas nesta execução. Registrar esse acesso e revisar a reserva antes de afirmar independência; a auditoria anterior de snapshots não cobria esse CSV.

Atualizações do protocolo e do congelamento devem ter nova versão/proveniência, preservando os documentos anteriores. O suplemento atual encerra pendências técnicas de obtenção e execução, não aprova automaticamente a entrada na etapa 6.

## Verificação e limites

A regressão de código mais recente permanece em **340 passed, 1 deselected**, com Ruff e mypy aprovados. Esta revisão acrescentou conferência de hashes e documentação; não alterou os arquivos de código nem repetiu testes sem necessidade. Redis, Docker, navegador e homologação completa continuam fora dos checks executados.

Reference-v1 preservada. Nenhum coeficiente ou limiar ajustado, candidata promovida, commit ou push. A etapa 6 permanece sem iniciar.
