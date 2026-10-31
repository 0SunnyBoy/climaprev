# Contratos instrumentais — revisão oficial em 28/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Esta revisão substitui a interpretação experimental de temperatura horária como instantânea, sem alterar o importador histórico congelado ou seus arquivos.

| Campo INMET automático | Semântica verificada / limite | Decisão no pipeline experimental |
|---|---|---|
| Temperatura do ar horária | Média da hora anterior | Importar intervalo como `observed_previous_hour_mean`; não parear com previsão instantânea |
| Máxima/mínima de temperatura | Extrema da hora anterior | Manter contratos próprios; amostras previstas instantâneas não viram extremas |
| Rajada máxima | Máxima da hora anterior | Janela temporal compatível com contrato horário de rajada; altura e representatividade por estação ainda não certificadas |
| Velocidade do vento | Média dos dez minutos anteriores | Não equiparar à velocidade prevista instantânea |
| Umidade horária | Definição refere a hora anterior sem explicitar agregação suficiente | Preservar intervalo com semântica não resolvida; comparação instantânea bloqueada |

Fonte primária: [glossário oficial INMET](https://portal.inmet.gov.br/glossario/nublado), consultado em 28/10/2026. O [Forecast API Open-Meteo](https://open-meteo.com/en/docs) distingue variáveis instantâneas e rajada máxima da hora anterior. A comparação exige igualdade de grandeza, intervalo e unidades, além de procedência adequada.

O CSV e o catálogo não fornecem, no material verificado, certificação de altura/calibração específica para cada instrumento de A201/A001/A801. Esses campos continuam desconhecidos: não presumir validação apenas por convenção de rede ou nome da variável.

## Efeito nos resultados anteriores

O protótipo publicado em `baa3465` expunha temperatura/umidade como amostras no endpoint, com limitação declarada de não certificar instrumento. A revisão oficial exige bloqueio mais forte. Relatórios dessa interpretação são checkpoints de desenvolvimento, não evidência de comparabilidade dessas grandezas. Nenhuma superioridade real da candidate-1 havia sido calculada ou aprovada a partir deles.

O parser experimental agora preserva a média térmica horária e a indefinição de umidade, e o comparador retorna ausência de casos equivalentes quando as previsões forem instantâneas. Não há média/interpolação artificial para forçar compatibilidade. Chuva e rajada seguem caminhos separados e explicitamente exploratórios.

Não usar `technical_pairing_ready` do perfil multivariável antigo para ativar o piloto. A nova qualificação de piloto primário verifica especificamente chuva recente e disponibilidade das fontes, sem exigir observações futuras já existentes ou liberar grandezas secundárias incompatíveis.
