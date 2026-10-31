# Acesso INMET — diagnóstico, obtenção e validação real

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Encerramento das pendências históricas — 20/10/2026

Os CSVs históricos oficiais de 2024 de A201/A001/A801 já foram obtidos e comparados. Isso não encerra a conectividade da API de avisos ativos: a nova tentativa em 20/10 teve RemoteProtocolError/conexão resetada. Obtenção de CSV e avisos em tempo real são dependências diferentes.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Resultado

O acesso foi restabelecido nesta execução. O CSV oficial A201/Belém de 2025 foi obtido, sua integridade ZIP foi conferida e o importador aceitou o formato real. As comparações de janeiro/2025 com GFS e ERA5 foram executadas para D+1, D+3 e D+7. Não houve ajuste de limiar, coeficiente ou início da etapa 6.

## Causa operacional identificada

DNS resolveu portal e API para `201.57.198.188`. A conexão TLS 1.2 completou com certificado validado. HTTP simples retornou redirecionamento para HTTPS. Portanto, as verificações atuais não apontam endereço inexistente, falha de resolução ou certificado inválido.

Foi realizado teste controlado com URL, método, Range e demais cabeçalhos iguais, alterando somente `User-Agent`, em duas rodadas:

| User-Agent | Rodada 1 | Rodada 2 |
|---|---|---|
| `python-httpx/0.28.1` | Conexão encerrada, `RemoteProtocolError` | Mesmo erro |
| Cabeçalho compatível com navegador | HTTP 206, 1.024 bytes | HTTP 206, 1.024 bytes |

**Conclusão:** o tratamento do User-Agent explica de forma reproduzível a diferença de acesso nesta execução. Isso é compatível com filtragem no serviço ou em um intermediário, mas não identifica qual equipamento/regra encerra a conexão nem prova a intenção de bloquear robôs. Não atribuir a causa a um firewall específico sem evidência adicional.

Também houve sucesso usando o cabeçalho de navegador com e sem leitura das configurações de proxy do ambiente. Nenhuma verificação TLS foi desabilitada e nenhuma credencial foi necessária.

Evidências: [diagnóstico DNS/TLS/HTTP](../planejamento/reference-candidate-1/evidence/diagnostico-acesso-inmet-retry.json) e [teste controlado de User-Agent](../planejamento/reference-candidate-1/evidence/comparacao-user-agent-inmet.json).

## Obtenção limitada do arquivo oficial

Fonte: [ZIP anual de 2025 publicado pelo INMET](https://portal.inmet.gov.br/uploads/dadoshistoricos/2025.zip), indicado no [portal de históricos](https://portal.inmet.gov.br/dadoshistoricos).

- ZIP remoto: 90.898.634 bytes.
- Entrada selecionada: `2025/INMET_N_PA_A201_BELEM_01-01-2025_A_31-12-2025.CSV`.
- Transferidos por HTTP Range: 337.832 bytes do ZIP, cerca de 0,37% do arquivo nacional.
- CSV descomprimido: 799.077 bytes, 8.760 registros horários.
- CRC32 conferido contra o diretório central ZIP.
- SHA256 do CSV: `2d2b3bbac55662a9d475c141819c0935401899644b862598560d551607d41621`.
- Destino local: `.historical-reports/inmet/A201-2025.csv`.

Os metadados do cabeçalho coincidem com os consultados na [API oficial de catálogo](https://apitempo.inmet.gov.br/estacoes/T): código A201, BELEM, latitude -1,41111111, longitude -48,43944444 e altitude 21,17 m. O encoding aceito foi CP1252.

Evidência: [proveniência da obtenção e catálogo](../planejamento/reference-candidate-1/evidence/obtencao-inmet-a201.json). O script reproduzível está em `.report-work/fetch_inmet_station.py`; recusa sobrescrever o CSV existente.

## Validação com dados reais

O importador foi executado contra o CSV oficial sem precisar alterar seu código. Janeiro apresentou 31 dias completos para chuva, rajada e temperaturas mínima/máxima nas janelas implementadas. Isso valida compatibilidade de formato, identidade e qualidade estrutural; não certifica calibração dos sensores nem representatividade espacial.

As distâncias da estação às grades retornadas são 10,333 km para GFS e 11,958 km para ERA5. O experimento mantém o ponto municipal original; não foi movido silenciosamente para a estação.

### Chuva diária frente à estação

Unidade: mm/dia; viés = fonte menos estação; 31 dias pareados em cada horizonte.

| Fonte | Viés | MAE | RMSE |
|---|---:|---:|---:|
| GFS D+1 | -2,381 | 10,052 | 13,589 |
| GFS D+3 | -4,100 | 11,416 | 14,673 |
| GFS D+7 | -8,365 | 13,313 | 19,190 |
| ERA5 | -2,448 | 10,939 | 14,821 |

ERA5 usa a mesma série nos três horizontes; sua linha é apresentada uma vez. Esses resultados demonstram que concordância com reanálise e erro frente à estação são avaliações diferentes. Não constituem avaliação de impactos ou da candidata.

Temperatura/rajada também foram comparadas nos três horizontes. Seus relatórios mantêm `calibration_ready=false`, por diferenças de amostragem/semântica e necessidade de revisão científica. Resumo estruturado: [validacao-estacao-real-a201.json](../planejamento/reference-candidate-1/evidence/validacao-estacao-real-a201.json). Relatórios completos estão em `.historical-reports/inmet/`.

## Divergência ainda não reconciliada

O CSV soma **427,6 mm** no janeiro civil de Belém e **427,0 mm** quando agrupado pela data UTC do timestamp. O [boletim mensal do INMET](https://portal.inmet.gov.br/uploads/Balan%C3%A7o_Janeiro25_Bel%C3%A9m.pdf) informa **417,0 mm** na automática.

Logo, a diferença com o boletim não foi explicada apenas pela troca entre essas duas convenções temporais. Pode exigir verificar revisões do arquivo, critérios de qualidade e cálculo do boletim; nenhuma dessas causas está confirmada. O relatório não substitui um valor pelo outro nem transforma essa divergência em coeficiente de correção.

## Atualização do estado das etapas 1 a 5

- Etapa 1: compatibilidade do importador com CSV oficial real e identidade A201 agora verificadas; revisão científica da qualidade permanece pendente.
- Etapa 2: comparação real de chuva executada para os três horizontes; representatividade e discrepância documental ainda exigem revisão.
- Etapa 3: comparações reais de temperatura e rajada executadas, mantendo limitações explícitas.
- Etapa 4: expansão 2024 permanece com 261 unidades local/data pareadas; não foi modificada nesta execução.
- Etapa 5: o congelamento técnico anterior foi preservado. As observações obtidas agora são evidência suplementar com hashes próprios, ainda não um novo congelamento científico aprovado.
- Etapa 6: **não iniciada**.

O ZIP/CSV anual de 2025 inclui dados de julho–dezembro, período reservado documentalmente para validação. O arquivo bruto anual foi obtido e lido estruturalmente pelo parser; nesta execução, somente janeiro teve resultados diários/métricas agregados e examinados. Isso deve ser considerado na futura auditoria de reserva: não afirmar que o arquivo de observações da validação jamais foi acessado. A auditoria anterior cobria somente snapshots `.inputs.json`, não este CSV adicionado depois.

Não houve alteração de código de produção, commit, push ou desativação da validação TLS. O acesso foi resolvido; a reconciliação do boletim e o aceite científico continuam pendentes.
