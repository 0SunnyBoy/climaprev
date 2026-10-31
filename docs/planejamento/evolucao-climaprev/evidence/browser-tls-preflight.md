# Preparação de confiança TLS no navegador

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../../projeto/STATE.md) · [RDP vigente](../../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

**Data:** 2026-09-13. **Resultado:** PASS para o mecanismo de teste isolado.
Esta prova usa um servidor HTTPS sintético temporário, não a stack Clima Prev.
O teste da entrada real permanece necessário em T20/T25.

Chrome 152, lançado visivelmente por Playwright com um perfil descartável:

1. Acesso HTTPS com CA desconhecida rejeitado com `ERR_CERT_AUTHORITY_INVALID`.
2. Inicialização do gerenciador de certificados no perfil temporário e
   fechamento do navegador antes de configurar a confiança.
3. CA sintética adicionada somente ao `Default/ServerCertificate` desse perfil.
4. Reabertura do mesmo perfil: HTTP 200 e corpo sintético esperado.
5. Navegador e servidor encerrados; chaves privadas sintéticas removidas.

Não foram usados `ignoreHTTPSErrors` ou flags de ignorar certificados. Nenhuma
CA foi instalada no perfil habitual do usuário ou no armazenamento do sistema.

Comando executado:

```bash
/home/ney/.nvm/versions/node/v24.16.0/bin/node /tmp/playwright-test-climaprev-ca-trust.js
```

Saída observada: `Unknown CA rejected`, `untrustedRejected=true`,
`trustedStatus=200`, `ignoreHTTPSErrors=false`.

A estrutura SQLite foi inspecionada no perfil descartável. Sua configuração
seguiu o [código do banco de certificados do Chromium](https://raw.githubusercontent.com/chromium/chromium/main/components/server_certificate_database/server_certificate_database.cc)
e o [schema de confiança](https://raw.githubusercontent.com/chromium/chromium/main/components/server_certificate_database/server_certificate_database.proto):
certificado DER, hash SHA-256 e metadado de CA confiável no banco do perfil.
O diálogo nativo de importação não gerou evento Playwright `filechooser`;
por isso a confiança foi provisionada no perfil fechado, mantendo a
verificação TLS normal. Este detalhe pertence ao harness de teste local,
não ao fluxo de uso do produto.
