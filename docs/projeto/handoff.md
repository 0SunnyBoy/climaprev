# ClimaPrev - Handoff de retomada

**Publicação e qualificação em 20/10/2026:** atualização enviada à develop; lote funcional `f0eab5e` aprovado em CI e Security gates. As correções de imagem/CSP passaram remotamente. Não houve merge em main ou deploy. Estado e pendências vigentes no [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md); descrições de alterações não enviadas/CI pendente abaixo pertencem aos lotes anteriores.

## Atualização vigente — 20/10/2026

Versão 0.1.0 de backend/frontend em desenvolvimento, branch develop na base 23bf4ce, com alterações sem commit/push. O [STATE](STATE.md) consolida implementações e evidências; o [RDP vigente](../../RELATORIO-PENDENCIAS-2026-10-20.md) define pendências.

Concluídos localmente: desacoplamento, janela UTC de sete datas, validade/cobertura conservadora de avisos, prazo global cooperativo, interface revisada, CI configurada, métricas por worker e campanha de carga. 644 testes backend e 27 frontend, checks estáticos/build e gate HTTPS aprovados; 3.000 requisições locais sem falhas. Resultados não aprovam produção ou candidata científica.

Ordem atual: (1) INMET real; (2) revisão/publicação do diff quando autorizada e CI remota; (3) revisão científica preparatória; (4) critérios de aprovação; (6 da lista original) acessibilidade manual. Por último, evolução da candidate-1 focada explicitamente em qualidade e precisão da previsão. Reference-v1 preservada; nenhum ajuste/calibração/promoção. Horizonte de 14 dias só planejado. Hospedagem adiada; monorepo mantido; não atualizar PDF acadêmico.

GitHub: CI da base passou; Security gates falhou no teste de tema. Correção local ainda sem rerun remoto; develop sem proteção/checks obrigatórios. Preservar alterações acumuladas, não incluir segredos/.homolog/dados brutos/artefatos locais no envio. Protocolos e evidências congelados não devem ser reescritos.

## Histórico

Os registros anteriores estão no [arquivo histórico](handoff-HISTORICO-ATE-2026-10-20.md). Eles não redefinem as prioridades ou o estado vigente.


## Próxima sessão de trabalho

1. Conferir `git status`, preservar alterações e ler o RDP antes de staging. Não executar `git add .` sem revisar arquivos e ignorados.
2. INMET: consultar `docs/operacoes/evidence/inmet-retomada-2026-10-20.json`; diferenciar conectividade da API de avisos e obtenção dos CSVs históricos, que já ocorreu. Não concluir causa de rede sem evidência.
3. CI: consultar `docs/operacoes/evidence/github-estado-2026-10-20.json`; falha remota foi tema no navegador. Correção de espera já existe localmente em `tests/docker/check_frontend_browser.py`; não alegar rerun do workflow antigo nem confundir runner Python com gate JS/Edge aprovado.
4. Manter revisão científica/aceite como preparação; não abrir outcomes reservados, escolher limiares ou ativar correção estatística.
5. Executar acessibilidade manual quando houver leitor de tela disponível; registrar ferramenta/versão, cenários e limitações. Não encerrar essa pendência com teste DOM automatizado.

A stack principal local fica em 8080/8000; Redis não exposto publicamente. As bancadas dedicadas de navegador/carga foram encerradas após os testes. Não reprovisionar secrets sobre diretórios existentes.
