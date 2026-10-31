# Revisão interativa no Edge — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Ambiente e escopo

Edge conectado pela extensão, aplicação local reconstruída em http://127.0.0.1:8080. Inspeção interativa de árvore de acessibilidade, teclado, foco, mensagens e captura visual; não é ensaio auditivo com NVDA/JAWS/Narrador nem certificação WCAG. As tentativas anteriores sem conexão foram superadas após o usuário adicionar o Edge. Firefox foi interrompido pela limitação de política de URLs da ferramenta; não foi usado como alternativa.

## Verificações realizadas

| Cenário | Resultado observado |
|---|---|
| Primeiro Tab e Enter | Atalho Ir para a consulta alcançado; Enter move foco para #consulta |
| Ordem de foco | Do atalho, Tab alcança modo de busca e campo Cidade |
| Falha real na busca | Mensagem e botão Tentar busca novamente visíveis; não confundidos com resultado vazio |
| Repetição por teclado | Tab alcança botão após blur do campo; Enter repete busca e devolve foco à Cidade |
| Emergência | Foco muda para #emergencia; Tab alcança retorno; Enter volta a #consulta e conserva Belém Pará no formulário |
| Idioma | PT/EN muda título, rótulos, mensagens já presentes e nome do botão de repetição; PT restaurado ao final |
| Tema | Controle exposto na árvore com estado; acionamento e tecla Espaço alternam tema; preferência escura inicial restaurada |
| Data obrigatória | Submissão sem data move foco ao campo; aria-invalid=true e descrição window-hint/start-date-error; mensagem Preencha este campo |

O papel do controle de tema apareceu como checkbox na árvore nativa e não coincidiu com a consulta DOM por role=checkbox. Usou-se o controle observado, que respondeu ao teclado; isso não comprova a experiência de fala do leitor de tela. O seletor de datas nativo pode conservar idioma do navegador/sistema mesmo com conteúdo da aplicação em inglês.

## Correção implementada

O blur da busca limpava a falha e removia o botão de repetição antes de o teclado alcançá-lo. Agora fecha sugestões/cancela trabalho atrasado, mas conserva a falha; ao repetir, foco volta ao campo. Escape, seleção e troca de modo continuam limpando o estado. Teste de regressão com foco real de elementos e 28 testes frontend aprovados; build/typecheck/ESLint aprovados.

## O que falta

Validar com leitor de tela real os anúncios de busca/carregamento/resultado/429/erros, ordem de leitura e navegação em PT/EN, inclusive na página de emergência e no modo de coordenadas. A inspeção descobriu um segundo defeito: resposta real sem correspondências omite results e inclui apenas generationtime_ms, sendo rejeitada pelo adaptador como 502. Corrigiu-se esse formato conhecido com validação finita/não negativa e mantendo rejeição de payloads malformados. API agora retorna 200/[] para Belém Pará e duas sugestões para Belém, Pará; orientação PT/EN passou a explicitar a vírgula. Repetição interativa no Edge confirmou mensagem vazia e seleção por seta/Enter. Na consulta real, a primeira tentativa atingiu deadline de 7 s (503, referência registrada) e uma repetição retornou previsão completa. Link de resultado moveu foco para #result; ida e volta da emergência preservou também o resultado, não apenas o formulário. Isso demonstra recuperação nesta amostra, não disponibilidade contínua.

[Evidência visual](evidence/acessibilidade-edge-2026-10-20.png) · [diagnóstico direto de geocoding](evidence/geocoding-durante-revisao-2026-10-20.json).

[Consulta real no Edge](evidence/consulta-real-edge-2026-10-20.png) · [API de busca após correção](evidence/geocoding-api-corrigida-2026-10-20.json).
