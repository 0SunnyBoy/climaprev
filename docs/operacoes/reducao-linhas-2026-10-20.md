# Redução de linhas e revisão das abstrações — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Resultado mensurado

Esta revisão reduziu **109 linhas físicas**, de **18.408 para 18.299**, sem apagar testes ou proteções. A comparação anterior com o commit `451d845` misturava responsividade, testes novos e refatoração, além de agrupar os testes do frontend com sua implementação. A tabela abaixo separa esses grupos e inclui arquivos novos e excluídos.

| Grupo | Commit 451d845 | Antes desta revisão | Depois | Variação desta revisão |
|---|---:|---:|---:|---:|
| Backend executável | 7.060 | 7.165 | 7.062 | −103 |
| Frontend executável | 1.770 | 1.801 | 1.795 | −6 |
| CSS e scripts Docker | 270 | 270 | 270 | 0 |
| Testes frontend | 450 | 524 | 524 | 0 |
| Testes backend e gates | 8.554 | 8.648 | 8.648 | 0 |
| **Total no mesmo escopo** | **18.104** | **18.408** | **18.299** | **−109** |

Código executável: **9.100 → 9.236 → 9.127**. Testes/gates: **9.004 → 9.172 → 9.172**. O saldo restante contra o commit é **+195 linhas**, das quais **168 em testes/gates e 27 em código executável**. Não houve redução líquida da série inteira em relação ao commit; houve redução comprovada nesta revisão.

Contagem inclui comentários e linhas vazias e exclui documentação/configurações, mantendo o escopo da pergunta anterior. Não mede complexidade ou desempenho por si só. [Contagem por arquivo e critérios](evidence/reducao-linhas-contagem-2026-10-20.json).

## Separação entre funcionalidades e estrutura

- **Funcionalidades anteriores:** encerramento de requisições travadas, cancelamento independente do transporte, recuperação da busca e correção do gate de hardening. Testes desses comportamentos foram mantidos.
- **Estrutura:** serviços específicos, DTOs, codecs, schemas, organização de testes, validação frontend e imports canônicos. Backend permanece praticamente do mesmo tamanho do commit (+2 linhas), com responsabilidades distribuídas.
- **Limite de atribuição:** não existe commit intermediário isolando responsividade e extrações. O frontend contém ambos; não se atribuiu artificialmente cada linha a uma intenção. As diferenças por área e a redução deste lote são exatas dentro do escopo declarado.

## Simplificações executadas

1. Mapeador HTTP: substituído o preenchimento repetitivo dos modelos internos por validação Pydantic dos atributos, mantendo explícitos os campos públicos, o request ID HTTP, a adaptação das datas e o fallback do resumo de risco. Schemas e validação permanecem; cache_status não é exposto.
2. Cache de previsão: removido método intermediário que só calculava a chave e encaminhava para outro método. Removidos três wrappers triviais de métricas e uma propriedade que apenas repetia `forecast.is_stale`; pontos de registro e comportamento mantidos.
3. Avisos: unificados os retornos após a escrita opcional de cache; supressão continua limitada à falha desse cache e não captura CancelledError. A validade ainda é conferida na entrega, inclusive quando o cache falha.
4. Frontend: representação estrutural de localização compartilhada por alias, eliminando interface com campos idênticos. Isso não remove validação JSON em execução.

Mantidos os serviços que isolam concorrência/expiração, a fronteira HTTP/domínio e o utilitário de prazo usado por duas operações. Fundi-los novamente reduziria arquivos, mas recombinaria responsabilidades e guardas já testadas. Não foram encurtados nomes, comprimidas instruções ou removidos testes para obter números menores.

## Equivalência e desempenho

JSON anterior/novo idêntico em **24 cenários sintéticos**, combinando unidades, completude, resumo de risco, alertas com validade opcional e medições ausentes. OpenAPI idêntico ao contrato anterior. [Evidência](evidence/reducao-linhas-equivalencia-2026-10-20.json).

Microbenchmark local do mapeador: um dia, 16,29 → 19,11 µs; sete dias, 34,11 → 32,50 µs. Cinco lotes de 200 chamadas, ordem alternada. Resultado misto, de poucos microssegundos: não demonstra melhoria geral de latência HTTP nem capacidade de produção. A simplificação é de manutenção, preservando o contrato, sem promessa de acelerar a API.

Validação completa: **659 testes backend aprovados em 55,18 s**, warnings como erros; **32 testes frontend**, build/tipagem/ESLint, Ruff e mypy Linux (75 módulos) aprovados. A primeira execução backend foi interrompida porque o Redis estava parado; não foi contabilizada como aprovação. Sem commit/push ou execução remota de CI.
