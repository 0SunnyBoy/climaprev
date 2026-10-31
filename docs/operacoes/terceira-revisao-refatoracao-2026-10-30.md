# Terceira revisão de refatoração — 30/10/2026

## Escopo e resultado

Executada após a revisão transversal e antes de commit/push, por solicitação do usuário. Foco independente: integridade do calendário D+7, completude do histórico do piloto, concorrência do orçamento, autorização em execução, resposta bruta e fronteiras dos dias civis. [Entrega consolidada](refatoracao-controle-d7-2026-10-30.md).

## Achados corrigidos

| Achado | Correção | Verificação |
|---|---|---|
| Datas ISO com offsets diferentes podiam representar o mesmo slot UTC e duplicar o universo planejado | Normalização e unicidade por instante UTC antes de construir os jobs | Dois textos para o mesmo instante são rejeitados |
| A presença de todas as datas semente não assegurava todos os pares estação/modelo nessas datas | Exigir o universo completo de pares da semente antes da auditoria de quota | Manifesto semente com par removido é rejeitado |

Essas mudanças pertencem exclusivamente aos módulos novos D+7. Não alteram os arquivos fingerprintados do piloto, seu calendário, cota ou ledger.

## Validação adicional

Suíte D+7 ampliada de 31 para **37 testes aprovados**. Acrescenta captura completa em dias locais de **23 e 25 horas**, trabalhadores independentes disputando o mesmo orçamento diário SQLite e execução sem E1 próprio bloqueada antes de HTTP/criação de ledger. Resposta de erro preserva bytes exatos, arquivos corrompidos são recusados e não há reabertura de reservas falhadas.

O inventário transversal anterior, o diff de runtime, os contratos de cache/HTTP e a nova divisão por responsabilidade foram conferidos novamente. Não foi identificado outro ponto que exija uma reorganização adicional antes da publicação deste lote. Isso não é garantia de ausência de defeitos ou de futuras oportunidades de manutenção.

## Limites e continuidade

Infraestrutura D+7 implementada, mas desativada; execução aguarda protocolo/calendário/E1 próprios e fim da quota de previsões do piloto. Fichas instrumentais individuais continuam ausentes. As funções científicas extensas pertencentes ao pipeline congelado permanecem oportunidades de revisão deliberada após o piloto, não remoção automática por tamanho.

Regressão integral posterior às correções: **1.207 testes backend**, Ruff e mypy em **102 módulos** aprovados; frontend permanece qualificado com **61 testes**, lint/tipagem/build, sem alteração após sua validação. O resultado é registrado na [evidência consolidada](evidence/refatoracao-controle-d7-2026-10-30.json). Nenhuma previsão real, fitting, promoção ou deploy foi executado nesta revisão. [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md).
