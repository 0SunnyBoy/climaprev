# Possível Plano de Evolução — ClimaPrev

**Natureza:** plano inicial de evolução. As propostas abaixo não representam
sozinhas o estado atual; consulte [STATE](STATE.md) e [ROADMAP](ROADMAP.md)
para o status atualizado em 18 de setembro de 2026. Itens já implementados
permanecem aqui como registro da origem do planejamento.

Este documento consolida o plano de evolução da ClimaPrev a partir da análise atual de arquitetura, backend, frontend, segurança, performance, testes e operação.

## Objetivos

- Consolidar a separação entre frontend estático e backend API.
- Tornar o ambiente de homologação consistente com o ambiente local.
- Melhorar segurança, observabilidade e previsibilidade operacional.
- Reduzir gargalos sob concorrência.
- Evoluir a qualidade e a confiabilidade das previsões de risco.

## P0 — Correções necessárias antes da homologação

### 1. Alinhar o Nginx de homologação

O backend deixou de servir o HTML e os assets. O Nginx de homologação deve passar a:

- Servir `index.html`, CSS e JavaScript diretamente.
- Encaminhar somente `/api/v1/risk` para o serviço `app`.
- Encaminhar `/health/` para o backend.
- Retornar 404 para rotas desconhecidas.
- Preservar os headers necessários para identificação da requisição e do cliente.

Validar o fluxo completo em `https://localhost:18443`:

- Página inicial com status 200.
- CSS com `Content-Type: text/css`.
- JavaScript com `Content-Type: application/javascript`.
- Consulta de risco funcionando pelo frontend.
- Health check funcionando.

### 2. Corrigir os testes de empacotamento

O teste de assets no wheel ainda espera encontrar arquivos em `climaprev/web`, embora o frontend tenha sido movido para a raiz do projeto e o `package-data` tenha sido removido.

Remover ou substituir esse teste por verificações do Nginx e da integração frontend/API.

### 3. Atualizar a documentação técnica

Revisar as referências antigas a `src/climaprev/web/` e à ideia de que o FastAPI serve a interface.

Arquivos que precisam ser revisados:

- `PROJECT.md`
- `docs/arquitetura.md`
- `docs/operations.md`
- `README.md`
- `Frontend-Rework.md`

Também revisar a regra do `.gitignore` que ignora arquivos `.md`, garantindo que a documentação necessária possa ser versionada.

### 4. Criar smoke tests do frontend e do Nginx

Adicionar testes automatizados para:

- `GET /` retornar o frontend.
- `GET /assets/styles.css` retornar CSS válido.
- `GET /assets/app.js` retornar JavaScript válido.
- `/api/v1/risk` ser encaminhado ao backend.
- `/health/` ser encaminhado ao backend.
- `/internal/*` não ficar público pelo frontend.
- Rotas inexistentes retornarem 404.
- Configuração passar em `nginx -t`.

## P1 — Segurança e estabilidade

### 5. Adicionar headers de segurança

Configurar no Nginx, avaliando a compatibilidade com o frontend:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy`
- `Content-Security-Policy`
- `Permissions-Policy`
- Proteção contra carregamento em iframe por meio de `frame-ancestors`

A política CSP deve permitir apenas recursos locais e o favicon `data:` atualmente utilizado.

### 6. Proteger endpoints administrativos

Revisar a exposição de:

- `/internal/metrics`
- `/docs`
- `/openapi.json`

Manter esses endpoints fora da exposição pública. Quando necessário, disponibilizá-los somente em rede administrativa, com autenticação ou por um exportador interno.

### 7. Corrigir identificação de clientes atrás do proxy

O Nginx local deve encaminhar corretamente os headers de proxy. O backend deve confiar nesses headers somente quando o proxy estiver explicitamente configurado como confiável.

Adicionar testes para garantir que:

- O IP real seja identificado corretamente.
- Um cliente não consiga forjar o `X-Forwarded-For` diretamente.
- O rate limit funcione de maneira justa atrás do Nginx.

### 8. Revisar o uso de dados na URL

A consulta atual usa GET e envia cidade ou coordenadas na query string. Avaliar a migração da consulta principal para:

```http
POST /api/v1/risk
```

com os parâmetros no corpo JSON. Isso reduz a exposição de localizações em histórico, logs e ferramentas de monitoramento.

### 9. Endurecer os containers

Aplicar aos serviços Nginx e Redis, quando compatível:

- Imagem fixada por versão e digest.
- `read_only: true`.
- `cap_drop`.
- `no-new-privileges`.
- Ausência de portas desnecessárias.
- Redes Docker com finalidade específica.

Manter autenticação no Redis em ambientes compartilhados e utilizar `rediss://` quando o Redis estiver fora da rede privada protegida.

### 10. Substituir polling agressivo do Redis

O fluxo de espera pelo lock consulta o Redis a cada 10 ms, podendo gerar muitas operações sob concorrência.

Substituir por uma estratégia com:

- Backoff exponencial.
- Jitter aleatório.
- Limite de tentativas.
- Deadline claramente definido.
- Métricas de contenção e timeout do lock.

## P1 — Observabilidade e performance

### 11. Evoluir as métricas

Substituir ou complementar as métricas em memória com Prometheus ou OpenTelemetry.

Medir pelo menos:

- Latência por rota.
- P50, P95 e P99.
- Taxa de erro.
- Respostas 429, 502 e 503.
- Cache hit, stale hit e miss.
- Contenção de locks.
- Latência por provedor.
- Falhas e retries por provedor.

Garantir agregação entre múltiplos workers.

### 12. Otimizar requisições ao provedor

Revisar os campos meteorológicos solicitados ao Open-Meteo e remover dados que não são utilizados na avaliação ou na resposta.

Isso reduz:

- Tamanho da resposta.
- Tempo de parsing.
- Uso de memória.
- Latência de rede.

### 13. Melhorar cache

Avaliar a quantização controlada das coordenadas da chave de cache para aumentar o reaproveitamento entre consultas geograficamente próximas.

Essa mudança só deve ser aplicada se a perda potencial de precisão for aceitável para o produto.

Também definir políticas de cache no Nginx:

- HTML com revalidação frequente.
- CSS e JavaScript com cache controlado.
- Assets versionados ou com hash para permitir cache longo com segurança.

### 14. Paralelizar operações independentes

Quando a integração de alertas oficiais estiver disponível, avaliar a execução paralela da busca de alertas e da previsão, desde que isso não prejudique consistência ou limites dos provedores.

Cachear alertas por localidade e período quando a validade dos dados permitir.

### 15. Definir limites explícitos no cliente HTTP

Configurar limites de conexões e concorrência do `httpx.AsyncClient` de acordo com a capacidade dos provedores e do serviço.

Manter:

- Timeouts de conexão, leitura, escrita e pool.
- Retry limitado.
- Não repetir indiscriminadamente respostas 429.
- Redirecionamentos desabilitados explicitamente para preservar a proteção contra SSRF.

## P2 — Evolução funcional

### 16. Integrar alertas oficiais

O sistema atualmente identifica que os alertas oficiais não estão configurados. A integração deve utilizar fonte autoritativa e apresentar:

- Órgão emissor.
- Área de cobertura.
- Data de emissão.
- Data de validade.
- Severidade.
- URL de origem.
- Estado de indisponibilidade ou atraso.

Alertas oficiais devem permanecer separados da avaliação heurística da ClimaPrev.

### 17. Calibrar cientificamente o risco

A política atual utiliza limiares absolutos e possui caráter orientativo. Evoluir com:

- Replay histórico.
- Comparação com eventos observados.
- Medição de falsos positivos e falsos negativos.
- Calibração por região e estação.
- Nível de confiança ou incerteza.
- Versionamento das políticas de risco.

Nunca apresentar a avaliação como substituta de alerta oficial ou avaliação local.

### 18. Melhorar a busca de localidades

Para resultados ambíguos:

- Retornar mais de uma opção.
- Solicitar estado, país ou região.
- Mostrar a localidade resolvida antes da consulta.
- Permitir confirmação do usuário.

### 19. Validar o horizonte de previsão

Definir e validar explicitamente o intervalo suportado pelos provedores. Retornar mensagens claras para:

- Data passada.
- Data além do horizonte disponível.
- Intervalo incompatível com o provedor.

## P2 — Evolução do frontend

### 20. Melhorar estados de interação

Adicionar:

- Timeout explícito no navegador.
- Botão de cancelamento.
- Estado de carregamento mais claro.
- Mensagens com `role="alert"` quando necessário.
- Melhor indicação de atualização de resultados.

### 21. Reexecutar auditoria de acessibilidade e performance

Após a migração para Nginx, executar novamente:

- Testes de teclado.
- Leitor de tela.
- Lighthouse.
- Verificação de contraste.
- Testes em telas pequenas.
- Testes de rede lenta.
- Testes de erro da API e rate limit.

## Qualidade e processo

### 22. Criar pipeline de CI

O pipeline deve executar:

- Ruff.
- Mypy.
- Testes unitários.
- Testes de integração.
- Testes Docker.
- Build da imagem de runtime.
- Validação do Nginx.
- Smoke test do frontend.
- Auditoria de dependências.

### 23. Criar documentação de operação

Documentar:

- Como subir o ambiente local.
- Como validar o frontend.
- Como validar a API diretamente.
- Como identificar falhas no Redis.
- Como interpretar métricas.
- Como renovar secrets.
- Como agir em caso de indisponibilidade do provedor.
- Como realizar rollback.

### 24. Registrar decisões arquiteturais

Criar ADRs para as decisões mais importantes:

- Separação do frontend e backend.
- Estratégia de cache e versionamento de chaves.
- Uso de locks distribuídos.
- Exposição dos endpoints administrativos.
- Integração de alertas oficiais.
- Evolução da política de risco.

## Ordem sugerida de execução

1. Ajustar homologação para servir o frontend.
2. Corrigir testes e documentação antigos.
3. Criar smoke tests do Nginx.
4. Adicionar headers de segurança e revisar endpoints internos.
5. Corrigir polling do Redis.
6. Melhorar métricas e criar baseline de performance.
7. Ajustar cache, compressão e versionamento dos assets.
8. Integrar alertas oficiais.
9. Calibrar o modelo de risco.
10. Evoluir desambiguação, horizonte de previsão e experiência do frontend.

## Critério de conclusão

A evolução poderá ser considerada concluída quando:

- Local e homologação utilizarem o mesmo modelo de entrega do frontend.
- Os testes de backend, Docker e Nginx estiverem automatizados.
- Não existirem referências à antiga localização `src/climaprev/web/`.
- Endpoints administrativos não estiverem publicamente expostos.
- Houver métricas de latência por percentil.
- O fluxo concorrente não depender de polling agressivo.
- A aplicação possuir fonte oficial de alertas ou declarar claramente sua ausência.
- O risco estiver documentado como avaliação orientativa e validado com dados históricos.
