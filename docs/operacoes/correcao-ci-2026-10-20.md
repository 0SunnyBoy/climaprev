# Correção dos gates remotos — 20/10/2026

## Diagnóstico do commit edb81b0

- [Validate application](https://github.com/0SunnyBoy/climaprev/actions/runs/39465912543): aprovado, mas o workflow CI falhou no job independente de HTTPS.
- HTTPS: procurava `climaprev-develop-app`, enquanto o checkout do GitHub construiu `climaprev-app`. Não era problema de senha de registry; a fixture dependia do nome da pasta.
- [Security gates](https://github.com/0SunnyBoy/climaprev/actions/runs/39465912612): espera do tema com `wait_for_function` bloqueada pela CSP, que não permite unsafe-eval. Aumentar o timeout não corrigiria essa causa.

## Correções

A fixture define `climaprev-api:decoupling-e2e`, build local target dev e pull_policy never. API e provedor usam essa imagem, construída pelo Compose da bancada. Nenhuma dependência do nome do projeto principal ou de imagem privada publicada. O teste de tema usa `expect(...).to_have_attribute`, preservando a verificação do DOM e o limite de espera. CSP e critérios de aceite não foram relaxados.

O upload da evidência HTTPS exige sucesso do passo de navegador da execução atual. No lote anterior, o job falhou antes do navegador e enviou a evidência local antiga versionada; esse artefato não comprova execução remota aprovada.

## Validação direcionada

Compose válido e actionlint local aprovados. Bancada HTTPS construída/iniciada pela própria configuração, sem tag derivada do checkout. Gate Python de navegador aprovado com Playwright 1.63 e Edge 155 em HTTP local (CSS, teclado/ARIA, tema/idioma, conteúdo sintético inerte). Gate JS entre origens HTTPS aprovado com API real e upstream sintético. Ambiente de teste local não substitui o runner Linux remoto ou a revisão manual com leitor de tela.

A suíte funcional anterior não foi repetida apenas por mudanças na bancada: aplicação backend/frontend não alterada. Aprovação para merge requer CI e Security gates concluídos com sucesso no mesmo commit. Não foi feito merge em main, deploy, ajuste de candidata ou ativação de 14 dias.
