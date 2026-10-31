# Frente 1 — Dados e integrações

Atualizado em 30/10/2026. Base funcional `ffa50f1`, versão 0.1.0. [Estado](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md).

## Refatoração revisada e infraestrutura D+7 — 30/10/2026

Limpeza de duplicações de handlers, campos do cache, limite de datas e montagem de consultas concluída. Segunda revisão transversal corrigiu a consulta duplicada no App; terceira revisão endureceu unicidade dos slots UTC e completude dos pares da semente, com 37 testes D+7 aprovados. D+7 agora tem três módulos separados: execução/calendário, transporte/arquivo bruto e ledger/orçamento. Implementação desativada, sem alterar o piloto, a API 14/7 ou a reference-v1. Execução D+7 aguarda protocolo/calendário/E1 próprios e conclusão da quota de previsões do piloto; não roda concorrentemente com ele.

Regressão local Linux: **1.207 testes backend**, Ruff e mypy em **102 módulos**; frontend Node.js 22: **61 testes**, lint/tipagem/build. OpenAPI preservado e cache equivalente à base. Redução de **42 linhas nos arquivos de runtime existentes**, com **461 linhas novas de D+7**; total no escopo medido cresce 419, sem alegação de redução global. Metadados instrumentais individuais ainda não comprovados, candidata sem superioridade demonstrada. [Entrega, revisão e limites](../operacoes/refatoracao-controle-d7-2026-10-30.md).

## Estado atual

Infraestrutura integrada pela develop2 e qualificada na develop: catálogo, coletores e normalização, arquivos imutáveis, manifestos/ledger, conversão TEMPO com proveniência e suporte à cobertura/pareamento. Observações recentes restauradas nas três estações; preflight 15/15 para D+1. Isso não comprova qualidade de previsão nem equivalência de todas as variáveis.

## Implementações e atividades pendentes

1. Operar o piloto v5 autorizado: coletar, auditar, repor perdas em novas datas e obter CSVs oficiais até a cauda observacional.
2. Entregar conjuntos elegíveis e rastreáveis por estação, variável e antecedência; explicitar ausência, rodada, qualidade e cobertura.
3. Complementar metadados instrumentais e corrigir incompatibilidades identificadas pela Frente 2 sem substituir medição por previsão/reanálise.
4. Manter os braços e contratos experimentais congelados; novas fontes/controle D+7 exigem versão deliberada e revisão das condições de uso. Duas APIs adicionais na previsão pública não são uma entrega concluída.

## Responsabilidades e limites

Frente 1 fornece dados e proveniência; Frente 2 define elegibilidade, avaliação e decisão científica. Cota de 210 capturas, reposições futuras e cauda até o último D+7 real não equivalem à campanha confirmatória. Reference-v1 permanece padrão. Hospedagem e separação de repositórios ficam fora desta execução.

[Registros anteriores](RELATORIO-CANDIDATE-1-FRENTE-1-DADOS-E-INTEGRACOES-REGISTROS-ATE-2026-10-30.md) · [Manual do piloto](../operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md).
