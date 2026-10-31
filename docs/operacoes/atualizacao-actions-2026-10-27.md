# Build Node.js 22 e atualização de Actions — 27/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Diagnóstico

O aviso de Node.js 20 refere-se ao runtime interno das ações antigas do GitHub Actions. A versão usada para compilar o frontend é uma configuração separada. A build do frontend foi reexecutada com Node.js 22.23.2, vue-tsc e Vite 6.4.5, com sucesso; saída local em frontend/dist (ignorada pelo Git).

O CI e o Security gates do commit 7b09fe6 concluíram com sucesso. CI: https://github.com/0SunnyBoy/climaprev/actions/runs/40542350613. Security: https://github.com/0SunnyBoy/climaprev/actions/runs/40542350627.

## Alterações dos workflows

- Checkout v7.0.1, setup-node v7.1.0 e upload-artifact v7.0.2, fixados por SHA oficial. Os três action.yml foram conferidos e usam node24.
- Runner Ubuntu 24.04 explícito nos dois workflows, evitando a migração automática de ubuntu-latest indicada pelo GitHub.
- Node.js 22 da aplicação e do runner de testes de navegador preservado.
- Permissões, gatilhos e gates de segurança preservados. Sem mecanismos para forçar runtime obsoleto.

As mudanças de workflows integram o envio de atualização para a develop solicitado pelo usuário. A qualificação exige CI e Security do commit que contém estes workflows; a aprovação do commit anterior não cobre esta atualização.

## Fontes oficiais

- https://github.com/actions/checkout/releases/tag/v7.0.1
- https://github.com/actions/setup-node/releases/tag/v7.1.0
- https://github.com/actions/upload-artifact/releases/tag/v7.0.2
