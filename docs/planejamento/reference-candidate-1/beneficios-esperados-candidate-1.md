# Candidate-1 — Benefícios esperados quando qualificada

Atualizado em 28/10/2026. Os benefícios abaixo descrevem a finalidade da candidata finalizada e qualificada, não ganhos já comprovados. A reference-v1 continua ativa e não foi demonstrada superioridade suficiente para substituí-la.

| Benefício | Como será obtido | Condição para poder afirmar o resultado |
|---|---|---|
| Menor erro de previsão | Correções/combinações avaliadas contra a baseline; objetivo inicial de pelo menos 5% de redução de MAE de chuva diária D+1 | Ganho em teste independente e critérios aceitos; não basta melhora em desenvolvimento |
| Menor viés sistemático | Diagnóstico do erro por local, variável e horizonte e refinamento com dados próprios de desenvolvimento | Viés medido e correção validada fora da amostra, sem piorar outras propriedades |
| Escolha fundamentada de fontes/modelos | Comparação com observações dos modelos individuais e alternativas de refinamento | Disponibilidade/licença compatíveis e origem meteorológica registrada; APIs distintas podem repetir um modelo |
| Avaliação mais ampla das condições meteorológicas | Chuva, temperatura, rajada e umidade com contratos e métricas próprios | Dados equivalentes, cobertura e suporte por alvo; não aplicar o critério da chuva às demais variáveis |
| Melhor tratamento dos extremos | Medir detecção, omissões e falsos alarmes, com proteções e incerteza | Suporte e metodologia adequados; menos falsos alarmes não pode ser prometido antes dos resultados |
| Classificação de risco mais fundamentada | Verificar separadamente como previsões refinadas afetam os indicadores calculados | Avaliar riscos com seu protocolo próprio; previsão meteorológica melhor não comprova automaticamente risco melhor |
| Tratamento explícito de dados parciais e antigos | Cobertura por fonte/variável, idade, exclusões e estados de indisponibilidade | Fluxo integrado e testado; não preencher falhas silenciosamente nem chamar dado vencido de atual |
| Comparações mais honestas | Mesmos casos, janelas e fontes observacionais, com denominador planejado | Não ocultar datas/horas ausentes de todos os braços ou selecionar apenas períodos favoráveis |
| Transparência e rastreabilidade | Preservar modelo, fonte, coleta/rodada, unidades, coordenadas, hashes e versões | Proveniência mantida na avaliação e na integração pública |
| Reprodutibilidade científica | Protocolo congelado, partições, dados arquivados, scripts e testes | Reservas independentes preservadas e critérios definidos antes da confirmação |
| Evolução regional e por horizonte | Identificar onde cada solução funciona melhor e onde há lacunas | Evidência suficiente em cada estrato; três estações não autorizam generalização nacional |
| Evolução mais segura da aplicação | Modelo/política versionados, regressões, contratos e possibilidade de retornar à versão anterior | Integração qualificada, sem substituir automaticamente a referência por um experimento |
| Inclusão futura de novas fontes com menor retrabalho | Adaptadores e normalização separados da avaliação e da API pública | Cada nova fonte ainda exige validação de contrato, origem, qualidade e condições de uso |
| Preservação da experiência da aplicação | Preparar coleta/processamento fora da requisição interativa, quando integrado | Medir latência e disponibilidade reais; a candidata não implica ganho automático de velocidade ou responsividade |
| Maior confiança para integrações e colaboração aberta | Evidências auditáveis e contrato estável para consumidores da API e colaboradores | Política de distribuição, atribuições e acesso compatíveis; código aberto não libera automaticamente uso comercial de endpoints gratuitos |

## O que já foi demonstrado tecnicamente

Infraestrutura experimental de coleta, proveniência, controles locais, pareamento de chuva, comparação numérica e cobertura está disponível. A continuidade de 28/10 acrescentou importação e pareamento experimental de temperatura/umidade/rajada, controle por janela planejada e reconciliação de Belém por versão. O preflight dos cinco braços nos três locais concluiu 15/15 consultas; os limites de cobertura por horizonte continuam explícitos.

Isso demonstra funcionamento desses componentes no escopo testado. Ainda faltam observações atuais verificadas, equivalência instrumental completa, avaliação de incerteza, refinamento e teste independente. Não há redução real de erro ou de falsos alarmes comprovada nesta entrega. Alertas oficiais continuam distintos dos indicadores calculados.

## Revisão de elegibilidade em 28/10/2026

A integração e os contratos foram revistos em fonte oficial: temperatura observacional média horária e agregação de umidade não resolvida não viram observações instantâneas. O pipeline bloqueia a comparação quando falta equivalência; este bloqueio é uma melhoria de integridade científica, não evidência de aumento da precisão. A verificação real continua sem pares contemporâneos para os alvos atuais. Ver [contratos](contratos-instrumentais-verificados-2026-10-28.md) e [relatório integrado](../../operacoes/frente-2-etapas-1-a-5-2026-10-28.md).
