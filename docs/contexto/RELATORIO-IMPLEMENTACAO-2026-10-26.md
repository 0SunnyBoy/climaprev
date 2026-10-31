# Relatório de implementação de 26 de outubro de 2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Resultado

Concluído o incremento técnico de baseline, identidade de rodada, controle local de campanha e pareamento exploratório de chuva com estação INMET. **714 testes backend, 33 frontend, mypy Linux em 81 módulos, Ruff e hardening local aprovados.** Alterações locais sobre `develop`/`5a6fc9c`, sem commit/push ou CI remoto deste lote. Reference-v1 e janela pública preservadas; nenhuma campanha científica iniciada ou candidata promovida.

## Implementações e finalidade

| Entrega | O que foi implementado | Para que serve |
|---|---|---|
| Baseline operacional | `tools/experimental_baseline.py` chama o próprio `OpenMeteoForecastClient` e o `RiskEvaluator` com `RiskPolicy` reference-v1; arquiva previsão normalizada, risco, identidade da política e código do adaptador | Comparar a candidata com a lógica vigente, sem substituir o controle por um modelo escolhido depois |
| Seleção automática rastreável | Envelope distingue modo automático de explícito; modelo e rodada desconhecidos continuam desconhecidos; não aceita rotular baseline automática como GFS/IFS conhecido | Evitar atribuição falsa de origem ou de independência |
| Rodada explícita | Coletor aceita inicialização UTC em ciclos suportados e usa o endpoint Single Runs; guarda parâmetros, resposta, horário solicitado e base de identificação | Reproduzir a rodada pedida e separar antecedência da inicialização de dias após a coleta |
| Manifesto | Identidade por campanha, slot, modelo e ponto/fuso; elimina repetições e aliases geométricos; registra família de origem e versões de código | Planejar coleta auditável, identificar fontes com origem comum e bloquear deriva de código sob o mesmo plano |
| Orçamento e deduplicação persistentes | Ledger SQLite com reserva transacional por job e limite por provedor/dia UTC; estado reservado, concluído ou falho | Dois executores locais não repetem a mesma chamada; falha ou execução interrompida não devolve cota nem autoriza retry automático |
| Execução por slot | Runner assíncrono sequencial exige ativação e autorização explícitas; ignora slot futuro/expirado e não faz backfill | Preparar agendamento controlado sem instalar ou iniciar uma rotina recorrente |
| Pareamento INMET | `tools/experimental_pairing.py` usa parser existente, verifica código e coordenadas da estação e compara chuva por intervalo exato no dia civil | Formar pares exploratórios com rastreabilidade e exclusões, sem comparar ponto municipal com estação silenciosamente |

O orçamento é compartilhado entre executores que usam **o mesmo arquivo local SQLite**. Não é quota empresarial, orçamento distribuído entre máquinas ou integração ao Redis de produção. Não compartilhar cronogramas independentes sem apontar para o mesmo ledger. Nenhum serviço de agendamento foi instalado; `enabled=False` e `collection_authorized=False` são os padrões.

## Limites importantes da baseline

A baseline cobre o **adaptador meteorológico de produção e a política ativa**, sem cache/stale, geocodificação, avisos oficiais ou toda a resposta da rota pública. O escopo fica no arquivo; não afirmar reprodução integral da experiência de uma consulta pública específica. A previsão normalizada preserva os campos e as regras do adaptador; este braço não arquiva o JSON bruto upstream.

O período deve permanecer na janela pública hoje UTC até +6. Portanto, o dia civil após coleta D+7 não possui baseline pública equivalente neste contrato; sua avaliação experimental precisa de controle separado e identificação no desenho. Não foi ampliado o produto para produzir esse comparador. `generationtime_ms` e atualização de feed não são inicialização do modelo.

## Identidade e disponibilidade

Verificação pontual em Belém: baseline aceita e arquivada; GFS global e IFS025 aceitos no Single Runs para inicialização `2026-10-25T00:00Z`. Essas consultas são diagnóstico de contrato, não campanha. Conteúdo completo ficou em `.report-work/implementation-2026-10-26/`, fora do Git.

O horário de inicialização vem do parâmetro explícito e do contrato do endpoint, registrado como `requested_single_run`; não é um timestamp ecoado/verificado independentemente no JSON. A coleta comprova disponibilidade **até aquele momento**, não horário exato de primeira publicação. As chamadas ao vivo genéricas e o MET continuam sem rodada atribuída quando ela não é comprovada. A seleção explícita MET é rejeitada antes de enviar HTTP.

Referências primárias consultadas: [Single Runs](https://open-meteo.com/en/docs/single-runs-api) e [disponibilidade dos modelos](https://open-meteo.com/en/docs/model-updates). A documentação distingue inicialização de disponibilidade e alerta que metadados de atualização não identificam automaticamente a mistura Best Match. Isso não aprova a precisão do modelo nem as reservas do projeto.

## Manifestos e retomada

`build_manifest` gera o plano e seu digest; `run_manifest` verifica schema, digest, versões do pipeline e correspondência do ponto antes de executar. Mudança nos módulos listados exige novo manifesto. Família ECMWF-IFS é compartilhada por IFS e MET global, sem descartar comparações entre seus tratamentos; família distinta também não é prova de independência estatística.

Reserva e cota são gravadas antes da tentativa. Um job reservado/falho não é repetido silenciosamente após reinício, inclusive quando não é possível saber se uma requisição interrompida chegou ao provedor. Recuperação/revisão de um lote exige decisão e nova identidade explícita; não apagar o ledger para contornar limites. O limite considera tentativas conservadoramente, não apenas respostas úteis.

As funções estão disponíveis para execução pontual programática e para um futuro acionador. Não há daemon, cron, serviço Windows, automação Codex ou calendário recorrente registrado. A coleta científica precisa dos parâmetros aprovados e de um acionador operacional antes de ser iniciada.

## Pareamento e execução exploratória

O pareamento calcula chuva somente se previsão e observação cobrirem integralmente o mesmo intervalo. Guarda hash do CSV e das medições, coordenadas, fuso, período por linha, motivo de exclusão e indicador de coleta anterior ao alvo. Campos ausentes não viram zero; previsão pontual/grade continua distinta de medida instrumental.

Executado replay do snapshot congelado `belem-2024-01-d1-station.inputs.json` com `A201-2024.csv`, de **01 a 28/01/2024**, janela exploratória já usada. Resultado técnico: 28 datas, nove pares completos e 19 excluídos por intervalo de previsão incompleto; zero casos com coleta anterior ao alvo, pois o snapshot é retrospectivo. Nenhum MAE, seleção de candidato ou ajuste calculado. Resultado completo ficou em `.report-work/pairing-2024-2026-10-26.json`.

Elegibilidade exploratória não é aprovação confirmatória: a coleta retrospectiva, a proveniência e a equivalência das variáveis continuam exigindo o desenho científico. Não foram abertos novos outcomes reservados. Temperatura, rajada e umidade não foram forçadas a compartilhar a convenção de chuva; pareamento dessas variáveis permanece pendente após adequação instrumental.

## Validação

- **714 testes backend passaram em 58,47 s**, warnings como erros, com Redis de teste e fontes/testes/docs atuais montados em Docker.
- **33 testes frontend**, ESLint, vue-tsc e build Vite aprovados, incluindo a correção local anterior do alerta 429.
- **Mypy Linux: 81 módulos sem erros. Ruff em `src` e `tests`: aprovado.**
- **Hardening local:** contrato aprovado no host pela configuração efetiva do Compose. Uma tentativa dentro da imagem da aplicação falhou por ausência do executável Docker; foi corrigido o local de execução, sem instalar ferramentas extras no runtime nem retirar o gate.
- Testes específicos cobrem baseline real via transporte simulado, janela pública, identidade automática, endpoint de rodada, ciclos inválidos/futuros, cotas persistentes, concorrência, deriva de manifesto/pipeline, horário e exclusões do pareamento.
- Verificações externas pontuais de baseline/Single Runs aprovadas; não equivalem a uptime ou qualificação de todos os modelos/locais.

Não executados neste incremento: CI remoto, homologação auditiva, campanha recorrente ou teste confirmatório de precisão. Sucessos antigos de GitHub não qualificam automaticamente este diff local.

## Pendências após esta entrega

1. Aceitar ou ajustar [parâmetros da campanha](../planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md): locais, duração, tolerâncias, suporte, critérios estatísticos e calendário.
2. Fechar controle de D+7 e política de rodada/disponibilidade, tratamento de entradas inválidas e dados parciais antes da campanha; não preencher chuva negativa ou períodos MET/ICON incompletos silenciosamente.
3. Preparar acionador e operação do ledger após aceite, sem iniciar coleta recorrente agora.
4. Completar pareamento de outras variáveis quando a equivalência observacional estiver definida e avaliar dados independentes conforme protocolo aprovado.
5. Só então comparar/refinar a candidate-1; integração depende de ganho comprovado e aceite separado.
6. Teste auditivo com leitor de tela e publicação do lote local com nova execução de CI/Security gates continuam pendentes.

Hospedagem definitiva, horizonte público de 14 dias e separação de repositórios continuam adiados. PDF/documento acadêmico não foi alterado.
