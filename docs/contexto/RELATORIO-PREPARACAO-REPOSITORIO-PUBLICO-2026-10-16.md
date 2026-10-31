# Relatório de preparação do ClimaPrev para publicação no GitHub

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Encerramento das pendências históricas — 20/10/2026

A preparação local inclui frontend/API independentes, gates de runtime/HTTPS, 644 testes backend e 27 frontend. Nenhum envio desta revisão ocorreu. Selecionar código/documentos e excluir segredos/dados brutos/artefatos locais antes de commits. Não confundir esta preparação com publicação de produto ou proteção ativa da develop.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Data:** 16/10/2026  
**Repositório:** [0SunnyBoy/climaprev](https://github.com/0SunnyBoy/climaprev)  
**Equipe:** quatro contribuintes, conforme informado pelo responsável.  
**Objetivo:** definir o trabalho necessário antes de mudar a visibilidade para pública, considerando a intenção de tornar o projeto open source.

## 1. Situação e limites deste relatório

Na análise de referência, o GitHub confirmou o repositório privado, com `main` como branch padrão e as branches `develop` e `old-develop`. Não foram encontrados `LICENSE`, `CONTRIBUTING.md` ou `SECURITY.md` na árvore remota de `main` examinada. Há mudanças e arquivos locais ainda não commitados.

**A preparação ainda não foi comprovada como concluída.** Este documento organiza pendências; não executa correções, não aplica uma licença, não publica arquivos e não muda a visibilidade. Não há aqui uma nova auditoria completa de segredos, histórico, imagens ou titularidade.

Base: [análise de licenciamento de 16/10/2026](RELATORIO-LICENCIAMENTO-OPEN-SOURCE-2026-10-16.md). Os achados devem ser reconfirmados no commit efetivamente escolhido para publicação.

## 2. Prioridades e responsáveis

As prioridades abaixo são critérios propostos para a equipe, não uma afirmação de que toda recomendação seja uma exigência legal.

- **P0 — resolver antes da abertura:** direitos, licença para o objetivo open source, informações sensíveis e condições de materiais de terceiros expostos.
- **P1 — concluir preferencialmente antes da abertura:** reprodução do projeto, distribuição dos artefatos, segurança e organização das contribuições.
- **P2 — melhoria posterior:** materiais de comunidade e apresentação que não bloqueiem a publicação responsável.

Os responsáveis são papéis sugeridos. A equipe deve atribuir cada atividade a uma pessoa e definir um revisor diferente quando possível.

| ID | Prioridade | Atividade | Responsável sugerido | Evidência de conclusão |
| --- | --- | --- | --- | --- |
| PUB-01 | P0 | Definir licença e registrar autorização dos titulares das contribuições existentes | Quatro contribuintes; administrador organiza | Registro individual de concordância, licença e escopo/commit identificados |
| PUB-02 | P0 | Revisar origem de código, documentos, imagens e dados de terceiros | Cada autor revisa seus materiais | Inventário com origem, permissão e decisão para cada material relevante |
| PUB-03 | P0 | Auditar segredos e informações sensíveis no conteúdo e histórico que serão expostos | Responsável por segurança | Resultado recente da varredura e revisão manual; achados tratados |
| PUB-04 | P0 | Revisar todas as branches, tags e superfícies GitHub expostas | Administrador e revisor | Lista das referências e conteúdos revisados, incluindo `old-develop` |
| PUB-05 | P0 | Adicionar licença oficial e declarar seu escopo | Mantenedor, após PUB-01 | `LICENSE`, README e metadados coerentes no commit aprovado |
| PUB-06 | P0 | Corrigir atribuição Open-Meteo e esclarecer condições dos dados publicados | Frontend e responsável por dados | Atribuição visível, documentação das fontes e condições de redistribuição |
| PUB-07 | P1 | Inventariar licenças e avisos dos componentes efetivamente distribuídos | Backend, frontend e infraestrutura | Inventário de terceiros e textos necessários presentes nos artefatos |
| PUB-08 | P1 | Identificar versão e licença exatas da imagem Redis fixada | Infraestrutura | Versão associada ao digest registrada e condições avaliadas |
| PUB-09 | P1 | Selecionar e validar o commit de publicação em ambiente limpo | Mantenedor e QA | Commit identificado, build e verificações aplicáveis aprovados |
| PUB-10 | P1 | Documentar instalação, testes, configuração e limitações | Equipe | README reproduzível e `.env.example` revisado |
| PUB-11 | P1 | Definir contribuição e canal de relato de vulnerabilidades | Mantenedores | `CONTRIBUTING.md` e `SECURITY.md` com instruções funcionais |
| PUB-12 | P1 | Revisar regras de branch, permissões e Actions | Administrador | Configuração efetiva conferida e revisão de PR definida |
| PUB-13 | P2 | Melhorar apresentação e organização da comunidade | Equipe | Descrição, tópicos, templates e código de conduta conforme necessidade |

**Estado inicial de todas as atividades:** pendente de execução ou de comprovação. Não marcar como concluído apenas porque já existe um arquivo ou workflow relacionado.

## 3. Direitos e licença — PUB-01, PUB-02 e PUB-05

1. Escolher entre os quatro contribuintes o objetivo de reutilização: ampla adoção, reciprocidade por arquivo ou compartilhamento de modificações em serviços web.
2. Usar a análise anterior para decidir a licença: Apache-2.0 é a recomendação inicial para reutilização ampla; AGPL-3.0 merece preferência se a reciprocidade em versões modificadas oferecidas pela rede for essencial. A decisão permanece em aberto.
3. Confirmar quem detém os direitos das contribuições. Diferentes nomes de commit podem ser aliases; autoria no Git não comprova titularidade. Verificar eventuais contratos com empresas ou instituições.
4. Registrar a autorização de cada titular sobre suas contribuições existentes, identificando licença e escopo. A administração da conta GitHub não substitui essa autorização.
5. Revisar os materiais referenciados em `docs/arquitetura/analise-referencias-sigfas.md`: esclarecer se houve cópia de conteúdo ou somente uso de ideias/estrutura, e documentar as permissões aplicáveis. Não presumir infração nem permissão.
6. Adicionar `LICENSE` com o texto oficial. Preencher identificação dos titulares onde aplicável, sem inventar titularidade coletiva ou transferência de direitos.
7. Atualizar README, `pyproject.toml` e `frontend/package.json` com a licença escolhida; manter lockfiles coerentes quando necessário. `private: true` no package.json pode continuar: esse campo evita publicação no npm e não controla a visibilidade no GitHub.
8. Especificar o que a licença cobre e quais materiais de terceiros possuem condições próprias. Se houver licença separada para documentação ou arte, declarar claramente seus caminhos e limites.

**Critério de conclusão:** o commit de publicação contém uma licença coerente, as autorizações estão registradas e não há material incluído com direitos de publicação não esclarecidos. Um DCO para contribuições futuras não regulariza automaticamente contribuições históricas.

## 4. Histórico, segredos e informações pessoais — PUB-03 e PUB-04

O `.gitignore` e o workflow de Gitleaks existentes são controles úteis, mas não comprovam que o histórico esteja limpo. Ignorar um caminho também não remove arquivos já versionados.

- Executar varredura com acesso ao histórico completo e às referências que serão expostas; confirmar a cobertura real das branches e tags, em vez de presumir que um job na branch padrão cobre tudo.
- Revisar manualmente `.env.example`, configurações, fixtures, scripts, documentos, screenshots e relatórios para localizar credenciais, dados pessoais, endereços internos ou informações de terceiros sem autorização de exposição.
- Revisar exceções do scanner, incluindo `.gitleaksignore`, para confirmar que não ocultam credenciais reais. Registrar resultados sem copiar valores sensíveis para o relatório.
- Incluir `main`, `develop`, `old-develop` e tags na decisão de publicação. Apagar um arquivo na versão atual ou remover uma branch não garante a eliminação das cópias e referências históricas.
- Revisar também releases, anexos de issues/PRs, wiki, logs e artefatos de Actions que possam ficar acessíveis com a mudança de visibilidade. Confirmar o comportamento de acesso de cada superfície.
- Se uma credencial real aparecer, revogar ou rotacionar com o responsável pelo serviço e verificar a invalidação. Avaliar depois a limpeza do histórico, coordenando qualquer reescrita com a equipe; ocultar o arquivo não invalida a credencial.
- Selecionar explicitamente os arquivos locais que entrarão na publicação. Há relatórios, CSVs, entregáveis e trabalho em andamento fora dos commits; evitar adicioná-los em lote sem revisão.

**Critério de conclusão:** cobertura documentada, revisão concluída e ausência de achados sensíveis não tratados nas superfícies a publicar. Não registrar “sem segredos” com base apenas na inspeção dos nomes de arquivos.

## 5. Fontes de dados e dependências — PUB-06, PUB-07 e PUB-08

### Open-Meteo e GeoNames

- Adicionar link de atribuição Open-Meteo próximo à apresentação dos dados; a interface examinada mostra apenas o identificador textual da fonte.
- Informar a licença dos dados e indicar as transformações aplicáveis, como a geração de estimativas de risco pelo ClimaPrev, sem sugerir endosso do provedor.
- Contemplar a origem GeoNames na geocodificação conforme as condições aplicáveis.
- Documentar que licença aberta do código e termos de acesso à API são assuntos separados. A API gratuita Open-Meteo restringe uso comercial; se houver operação comercial, escolher acesso autorizado antes dessa operação. A simples abertura do repositório não exige contratar um plano comercial.

### INMET e datasets

- Identificar origem, endpoint, data de coleta e condições de uso dos dados e alertas efetivamente utilizados ou redistribuídos.
- Esclarecer permissões antes de incluir CSVs, datasets ou outros materiais de terceiros no repositório. Se as condições de um dataset não estiverem esclarecidas, manter sua redistribuição fora do escopo da publicação até resolver o ponto.
- Preservar avisos e atribuições aplicáveis; não atribuir automaticamente aos dados a licença do código próprio.

### Bibliotecas e imagens

- Consolidar nomes, versões, licenças e avisos das dependências Python, JavaScript e dos componentes de imagens distribuídas.
- A análise preliminar encontrou licenças permissivas no lockfile JavaScript e componentes MPL-2.0 no ambiente Python, incluindo `certifi` e `pathspec`. Verificar os arquivos e obrigações da distribuição concreta; não substituir essa revisão por uma contagem de identificadores.
- Preparar `THIRD_PARTY_NOTICES.md`, ou equivalente, com inventário e os textos/avisos necessários. Links isolados não substituem textos que precisem acompanhar uma distribuição. Criar `NOTICE` quando houver conteúdo ou obrigação aplicável, sem tratá-lo como requisito universal.
- Verificar wheels, frontend compilado e imagens Docker para garantir que os avisos acompanhem o produto entregue. Distinguir imagens de runtime, desenvolvimento e carga.
- Resolver a versão menor do Redis associada ao digest fixado no Compose. Não presumir BSD pelo tag `redis:7-alpine`. Se a equipe considerar uma alternativa, como Valkey, avaliar compatibilidade e manutenção antes de mudar.

**Critério de conclusão:** as condições dos materiais expostos e dos artefatos oferecidos estão documentadas e atendidas. Se um artefato ainda não passou pela revisão de distribuição, não oferecê-lo como release aprovada; registrar o limite de escopo.

## 6. Qualidade, documentação e colaboração — PUB-09 a PUB-12

- Definir qual commit de `main` será publicado e quais alterações de `develop` serão promovidas. Não misturar a abertura com mudanças locais ainda sem validação.
- Validar em clone limpo usando as instruções públicas: instalação/build, execução e verificações relevantes. Aproveitar CI e testes existentes e registrar o resultado no commit selecionado; não é necessário repetir verificações já válidas sem mudança ou motivo.
- Documentar pré-requisitos, execução com Docker, endereços locais, configuração, testes e limitações conhecidas. Usar exemplos sintéticos e instruções para geração local de segredos.
- Preservar o aviso de que o risco é uma estimativa e não substitui alertas oficiais; informar limitações de dados, disponibilidade e calibração sem apresentar capacidade não validada como pronta.
- Criar `CONTRIBUTING.md` com fluxo de branches/PRs, verificações esperadas, licença das contribuições e política de origem. Decidir se será usado sign-off/DCO; um CLA amplo só deve ser adotado se houver necessidade concreta.
- Criar `SECURITY.md` com canal privado válido para vulnerabilidades e versões atendidas. Não orientar a publicação de credenciais ou detalhes exploráveis em issues abertas.
- Revisar rulesets/proteção da branch principal, revisão obrigatória quando adequada, checks de CI e permissões dos quatro mantenedores. O resultado anterior indicou `protected: false` nas branches, mas regras adicionais não foram auditadas.
- Revisar permissões de Actions, exposição de secrets e execução de código de PRs externos, especialmente workflows privilegiados. Conferir as configurações efetivas disponíveis para a conta/repositório.

**Critério de conclusão:** uma pessoa consegue reproduzir o projeto pelas instruções publicadas, os resultados de validação estão vinculados ao commit e há um processo claro para contribuições e relatos de segurança.

## 7. Sequência de execução

1. **Definir o escopo:** escolher commit, branches, arquivos e artefatos candidatos à publicação.
2. **Resolver direitos e sensibilidade:** executar PUB-01 a PUB-04 e esclarecer os materiais externos em PUB-06.
3. **Preparar o conteúdo:** concluir licença, atribuições, inventário e documentação; abrir PRs internos para revisão das mudanças.
4. **Validar o candidato:** verificar artefatos oferecidos, CI, reprodução em clone limpo e configurações de colaboração.
5. **Registrar a decisão da equipe:** preencher o quadro de liberação abaixo com evidências e pendências aceitas.
6. **Mudar a visibilidade:** o administrador realiza a alteração após a decisão registrada.
7. **Conferir a experiência pública:** verificar acesso sem autenticação, licença detectada, links, instruções e ausência de conteúdo inesperado. Se algo sensível aparecer, tratar o incidente imediatamente; voltar a privado não recupera cópias já feitas.

## 8. Registro de liberação

Preencher somente após executar as atividades. Os campos abaixo são deliberadamente deixados em aberto.

| Campo | Registro |
| --- | --- |
| Commit aprovado para publicação | A definir |
| Branches e tags que permanecerão acessíveis | A definir |
| Licença e escopo aprovados | A definir |
| Autorizações dos quatro titulares/contribuintes | Vincular evidências e esclarecer titularidade |
| Revisão de materiais de terceiros | Vincular inventário e decisões |
| Varredura de segredos e cobertura do histórico | Vincular resultado, data e referências cobertas |
| Revisão manual e superfícies GitHub | Vincular registro sem valores sensíveis |
| CI e reprodução em ambiente limpo | Vincular resultados do commit aprovado |
| Distribuições/releases incluídas na abertura | Listar ou declarar que não fazem parte do escopo |
| Pendências P1/P2 aceitas, responsável e prazo | A definir |
| Decisão final e administrador responsável | A definir |

**Critério proposto para liberar:** todos os P0 concluídos e comprovados; P1 concluídos ou com pendência explicitamente aceita pela equipe e escopo ajustado quando necessário. Nenhuma exceção pode conceder direitos que a equipe não possui ou dispensar obrigações de terceiros.

## 9. Referências

- [Relatório de licenciamento e evidências do projeto](RELATORIO-LICENCIAMENTO-OPEN-SOURCE-2026-10-16.md).
- [GitHub — licenciar um repositório](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
- [Open Source Guides — direitos e contribuições](https://opensource.guide/legal/).
- [Open-Meteo — licença e atribuição](https://open-meteo.com/en/licence) e [termos da API](https://open-meteo.com/en/terms).
- [Redis — licenças por versão](https://redis.io/legal/licenses/).
- [DCO — certificado de origem](https://developercertificate.org/).

As condições externas foram consultadas na análise de referência de 16/10/2026 e devem ser reconfirmadas se a publicação ocorrer posteriormente ou se os componentes e provedores mudarem.
