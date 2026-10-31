# Frente 2 — Ciência, precisão e integração

Atualizado em 30/10/2026. Base funcional `ffa50f1`, versão 0.1.0. [Estado](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md).

## Refatoração revisada e infraestrutura D+7 — 30/10/2026

Limpeza de duplicações de handlers, campos do cache, limite de datas e montagem de consultas concluída. Segunda revisão transversal corrigiu a consulta duplicada no App; terceira revisão endureceu unicidade dos slots UTC e completude dos pares da semente, com 37 testes D+7 aprovados. D+7 agora tem três módulos separados: execução/calendário, transporte/arquivo bruto e ledger/orçamento. Implementação desativada, sem alterar o piloto, a API 14/7 ou a reference-v1. Execução D+7 aguarda protocolo/calendário/E1 próprios e conclusão da quota de previsões do piloto; não roda concorrentemente com ele.

Regressão local Linux: **1.207 testes backend**, Ruff e mypy em **102 módulos**; frontend Node.js 22: **61 testes**, lint/tipagem/build. OpenAPI preservado e cache equivalente à base. Redução de **42 linhas nos arquivos de runtime existentes**, com **461 linhas novas de D+7**; total no escopo medido cresce 419, sem alegação de redução global. Metadados instrumentais individuais ainda não comprovados, candidata sem superioridade demonstrada. [Entrega, revisão e limites](../operacoes/refatoracao-controle-d7-2026-10-30.md).

## Estado atual

Infraestrutura científica integrada: protocolo/partições, pareamento e comparação, critérios, cobertura, bootstrap/incerteza, revisão instrumental declarada, famílias de comparações e variantes fixas de combinação/correção. Relatório do piloto disponível. Direção e parâmetros operacionais fundamentados receberam aceite delegado; piloto v5 autorizado. Suporte real, equivalência instrumental e validade inferencial continuam condicionais.

## Implementações e atividades pendentes

1. Analisar cobertura e viabilidade do piloto quando houver capturas e observações elegíveis.
2. Fechar contratos instrumentais, suporte de extremos, bloco e multiplicidade; avaliação exploratória não certifica confirmação.
3. A infraestrutura do controle D+7 está implementada; preparar protocolo/calendário/E1 próprios após a quota do piloto e replanejar partições antes da análise, se necessário. A nova API 14/7 não altera a baseline congelada do piloto.
4. Ajustar e comparar variantes somente no desenvolvimento, selecionar nas partições próprias, congelar e confirmar fora da amostra.
5. Apresentar evidência para aceite final e integrar candidata apenas se aprovada, com rastreabilidade, contratos e regressão. Não há ganho demonstrado ou promoção.

## Responsabilidades e limites

Frente 1 fornece dados e proveniência; Frente 2 define elegibilidade, avaliação e decisão científica. Cota de 210 capturas, reposições futuras e cauda até o último D+7 real não equivalem à campanha confirmatória. Reference-v1 permanece padrão. Hospedagem e separação de repositórios ficam fora desta execução.

[Registros anteriores](RELATORIO-CANDIDATE-1-FRENTE-2-CIENCIA-E-PRECISAO-REGISTROS-ATE-2026-10-30.md) · [Manual do piloto](../operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md).
