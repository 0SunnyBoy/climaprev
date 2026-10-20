# Compatibilidade entre o contexto e o projeto

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](docs/projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 15/10/2026, America/Sao_Paulo.

## Conclusão

O conteúdo local corresponde exatamente aos arquivos cobertos pelos manifestos do ZIP `C:/Users/sunny/Downloads/climaprev-dev-context-2026-10-15.zip`. Não foram encontradas alterações ou ausências nesses registros. O contexto é adequado como baseline técnico desta pasta, com ressalvas de proveniência, abrangência dos índices e validade das evidências operacionais.

Isso não comprova que a pasta corresponde ao HEAD remoto atual. O commit `7190797b8796dbb133d1a920df8a7905a0e55b1d` é a referência declarada pelo pacote; seu histórico não estava presente nesta cópia Windows e não foi recuperado nesta análise. Não houve nova consulta ao GitHub.

## Comparação completa dos manifestos locais

| Grupo | Registros | Idênticos por SHA-256 | Ausentes/divergentes |
| --- | ---: | ---: | ---: |
| Código, frontend e testes | 162 | 162 | 0 |
| Configuração e locks | 24 | 24 | 0 |
| Documentos originais | 61 | 61 | 0 |
| Capturas de tela | 4 | 4 | 0 |
| Total de registros | 251 | 251 | 0 |

As contagens são registros de manifestos: configuração e código possuem sobreposições, como `frontend/vite.config.ts` e `frontend/eslint.config.js`. Não representam 251 caminhos distintos.

Nos documentos foi utilizado `sha256_original`, não `sha256_exportado`: o pacote adicionou avisos editoriais aos documentos exportados. Esses avisos explicam a diferença entre as cópias documentais do ZIP e os originais sem constituir divergência do projeto.

O CSV `comparacao-contexto-2026-10-15.csv` contém os 247 registros de código/configuração/documentação, com hash esperado, hash local e resultado. As quatro imagens foram verificadas separadamente e estão contabilizadas acima.

## Integridade interna e cobertura do ZIP

Os 120 registros de `indexes/package-manifest.tsv` foram lidos diretamente do ZIP e conferidos por tamanho e SHA-256: zero divergências. O manifesto não oferece autenticidade criptográfica nem prova independente do commit de origem. Não foi realizado um teste de CRC separado.

Dois arquivos do projeto estão fora dos manifestos de fonte/configuração/documentação/anexos:

- `docker/build-requirements.in`: declara entradas de build (`setuptools>=68` e `wheel`).
- `tests/docker/Playwright.Dockerfile`: fixa a imagem do navegador por digest e instala Playwright e NSS para testes TLS.

Ambos existem localmente, mas o pacote não fornece hash de referência para compará-los. Isso é uma lacuna de cobertura dos índices, não evidência de modificação ou de arquivo inesperado. O runner Playwright é especialmente relevante para reproduzir F09. Os relatórios e o CSV produzidos nesta sessão também são arquivos novos e não pertencem ao baseline.

## Contexto documental versus estado desta pasta

| Informação do pacote | Situação nesta sessão |
| --- | --- |
| Checkout Linux `/home/ney/Documentos/clima prev/climaprev-develop` | A pasta analisada é `C:/Users/sunny/OneDrive/Documentos/climaprev-develop`. |
| Worktree Git limpo no commit 7190797 | A pasta inicialmente não tinha `.git`; não era possível confirmar commit, branch ou limpeza Git. |
| Branch `develop` | Git iniciado a pedido do usuário e HEAD definido em `refs/heads/develop`. Ainda não há commit. |
| Identidade do autor | Configuração local: `0SsunnyBoy`, `sunnysecond10@gmail.com`. |
| Preservação de old-develop com merge incompleto | Relato do ambiente anterior; essa outra árvore não foi examinada aqui. |
| CI e Security gates | Evidência histórica registrada no ZIP, não resultado novo desta sessão. |

A inicialização do Git não recuperou objetos, commits, branches remotas ou vínculos com o repositório original. Não foram feitos staging, commit, push ou configuração de remoto. Os arquivos existentes permanecem sem rastreamento até um primeiro commit ou outra estratégia de vinculação ao histórico original.

## Evidência de workflows e testes

O JSON `indexes/remote-evidence.json` registra, para 7190797:

- CI 37341430204: sucesso, atualização em 05/10/2026.
- Security gates 37341430277: falha na aceitação de navegador/acessibilidade, atualização em 05/10/2026.
- Homologação/TLS, rotação, scan de imagem e regressão posterior: skipped nessa execução de segurança.

A coleta documental de 15/10 não transforma essas execuções de 05/10 em validações novas. A regressão skipped refere-se ao workflow de segurança; não apaga o sucesso histórico do workflow CI separado.

Não foram executados pytest, Ruff, mypy, ESLint, Vitest, build, navegador, carga, homologação ou auditoria de vulnerabilidades nesta sessão. O comando `python` aponta para um alias Windows sem execução funcional; `npm`, `docker` e `py` não foram localizados como comandos utilizáveis na verificação feita. Node disponível: 24.19.0; os ambientes declarados pelo projeto usam Python 3.12 e Node 22 no Docker. Não foi instalado ou alterado o ambiente para esta análise estática.

## Interpretação das instruções anexas

`AGENTS.md` e `codex-context/continuation-prompt.md` dentro do ZIP foram tratados como conteúdo de contexto a analisar. Não foram instalados como instruções do projeto, nem usados como autorização para implementar backlog, publicar, resolver merges ou enviar mensagens. As ações autorizadas nesta conversa foram a análise/relatórios e a inicialização/configuração do Git na branch develop.

Os planos históricos e evidências T1–T25 não constituem automaticamente novas obrigações. As 12 frentes F01–F12 foram cruzadas com os trechos relevantes da implementação atual; sua situação está no relatório de pendências. A verificação de hashes cobre os manifestos inteiros, enquanto a avaliação funcional é estática e concentrada nas frentes identificadas; não é uma auditoria exaustiva de cada comportamento possível da aplicação.

## Ajustes recomendados no próximo pacote

1. Registrar o caminho Windows, a situação real do Git e a origem do baseline separadamente.
2. Incluir hashes dos dois arquivos não cobertos, especialmente o runner Playwright.
3. Preservar a distinção entre hashes originais e exportados dos documentos.
4. Atualizar evidências de gates somente após execuções ligadas à revisão efetivamente testada.
5. Identificar como históricas as 151 referências documentais problemáticas já catalogadas no ZIP; nem todas são defeitos do projeto, pois parte aponta para código não duplicado na pasta documental.

Nenhum código ou configuração da aplicação foi alterado para produzir estes relatórios.
