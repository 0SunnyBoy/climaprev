# Planejamento de extração — ClimaPrev-API

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Data: 28/10/2026. Destino: `0SunnyBoy/ClimaPrev-API`, inicialmente privado e vazio. Este documento planeja a execução; não cria branch, checkout, commit ou publicação.

## Objetivo e primeira entrega

Entregar o backend como projeto instalável e executável por conta própria, sem árvore de frontend, ferramentas Node.js ou arquivos locais do General-ClimaPrev. Preservar a API pública existente e a reference-v1 ativa. Separação de repositórios não significa, por si só, que todos os requisitos de um serviço comercial estejam concluídos.

A candidate-1 permanece no projeto geral enquanto experimental. Sua confirmação científica não é pré-requisito para extrair uma API baseada na versão estável existente.

## Estratégia Git recomendada

**Usar uma branch local de extração, em um clone separado do repositório da API.** Nome proposto: `codex/climaprev-api-extraction`.

Uma branch no checkout atual não isola arquivos ainda não commitados. Há trabalho da Frente 2 em andamento na develop; não trocar sua branch, mover arquivos, descartar alterações ou usar stash para executar esta extração.

O clone da API terá configuração Git própria: `origin` apontando exclusivamente para `https://github.com/0SunnyBoy/ClimaPrev-API.git`. O checkout oficial continuará com seu origin oficial; após a renomeação, ele será atualizado para General-ClimaPrev na tarefa correspondente. Não substituir o origin oficial pelo destino da API.

Recomendação de importação: primeiro commit próprio, com arquivos selecionados de um snapshot qualificado, registrando origem e autoria. Não enviar automaticamente todo o histórico, branches, evidências ou arquivos do projeto geral. Essa opção exige manter registro de proveniência; não será possível tratar os dois históricos como se fossem a mesma branch após a separação.

Fluxo:

1. Registrar o SHA de origem do projeto geral e exportar apenas os arquivos escolhidos.
2. Montar e validar o projeto na branch local `codex/climaprev-api-extraction`, no clone separado.
3. Revisar o diff de importação, os arquivos e os resultados antes do primeiro push.
4. Como o destino está vazio, criar sua primeira main com o snapshot completo já validado; não existe main com código para receber PR antes desse bootstrap. Fazer o envio explicitamente para o repositório da API.
5. Adotar main estável e develop para integração no derivado; mudanças seguintes usam branches de trabalho e PRs próprios.

Não usar push com mirror, force ou envio indiscriminado de todas as branches do oficial.

## Base da extração

O HEAD observado nesta análise é `6576dd6821bf882e9883e7d82b762927dabb6dbd`; os registros anteriores apontam CI/Security aprovados para essa versão. O diff local posterior da Frente 2 está em andamento e não pertence a esse SHA.

Antes da execução, escolher e registrar uma das bases:

- **Extração independente imediata:** partir do commit publicado qualificado, preservando reference-v1 e excluindo ferramentas de pesquisa do pacote da API.
- **Extração após consolidar o lote atual:** aguardar um commit específico com o lote revisado e checks próprios aprovados, sem incorporar arquivos locais parcialmente implementados.

Preferência: uma base publicada e qualificada explicitamente escolhida. Não copiar o diretório de trabalho atual como se fosse um snapshot validado. Mesmo escolhendo uma base com experimentos, somente dependências operacionais necessárias serão incluídas.

## Etapas e implementações

| Etapa | Implementações | Entrega / critério de conclusão |
|---|---|---|
| 1. Inventário e proveniência | Mapear imports do runtime, arquivos de build/configuração e testes; identificar licenças/atribuições; fixar SHA e política de risco de origem | Manifesto de extração com allowlist, exclusões e justificativas; nenhum arquivo de pesquisa incluído por acidente |
| 2. Projeto autônomo | Importar domínio, aplicação, API, infraestrutura, runtime e configurações necessários; manter imports internos estáveis; preparar dependências de produção/build/desenvolvimento com locks | Pacote Python instalável a partir de um clone limpo; runtime sem imports de ferramentas experimentais ou necessidade de frontend |
| 3. Build e operação | Adaptar Dockerfile, Compose, healthchecks, logs, Redis, métricas e exemplos de ambiente | Build e execução independentes; nenhum extends, COPY, volume ou caminho apontando para arquivos ausentes do monorepo |
| 4. Contrato e documentação | Preservar endpoints, validações, erros, unidades e regras; documentar instalação, parâmetros, CORS e consumo externo | Cliente externo consegue consultar a API segundo contrato; mudanças de contrato não são misturadas à extração |
| 5. Testes e segurança | Portar os testes operacionais necessários, criar CI próprio, adaptar gates de hardening e executar auditorias | Testes, lint, tipagem, build, hardening e verificações de dependências/segredos passam no novo projeto |
| 6. Publicação privada | Revisar árvore e diff final; registrar versão/origem; enviar a primeira main validada e preparar develop | CI/Security do SHA do derivado aprovados; checkout limpo; instalação reproduzível sem acesso ao projeto geral |

## Arquivos: incluir, adaptar e excluir

### Incluir conforme inventário de imports

- `src/climaprev/domain`, `application`, `api`, `infrastructure` e módulos operacionais de runtime/configuração/logs/erros/saúde.
- `pyproject.toml`, README próprio e locks necessários a produção, build e desenvolvimento.
- Testes de domínio, API, provedores, cache, concorrência, limites, saúde e segurança correspondentes ao código importado, com seus suportes/fixtures.
- Exemplos de ambiente sem credenciais, documentação operacional relevante e avisos de origem/atribuição.

Essa lista é orientação de inventário, não autorização para apagar arquivos do oficial nem substituir a análise de dependências transitivas.

### Adaptar obrigatoriamente

1. **Compose:** hoje `docker-compose.api.yml` usa extends de `docker-compose.yml`. No derivado, preferir um Compose próprio e completo para app/Redis, redes, healthchecks e hardening, sem necessidade do Compose do projeto geral.
2. **Dockerfile:** o estágio dev atual copia tests, docs e requirements-load.lock. Ajustar os estágios para a árvore efetivamente incluída, preservando build reproduzível e imagem de runtime com usuário sem privilégios. Ferramentas de carga, se mantidas, ficam separadas da imagem de produção.
3. **CI:** os workflows atuais constroem e testam Vue/Nginx e executam bancada frontend/API. Criar gates específicos do backend. Validação HTTPS/CORS deve usar cliente ou fixture externa de teste, sem exigir o código do frontend do projeto geral.
4. **Hardening:** os scripts atuais também verificam serviços frontend/redis-load. Adaptar as verificações à topologia da API sem remover proteções equivalentes de app/Redis.
5. **Metadados e links:** README, proveniência e identificação HTTP dos provedores devem apontar para o produto/repositório correto. Preservar nome de importação `climaprev` inicialmente; renomear pacote seria outra alteração de compatibilidade. Revisar identificação do pacote antes de eventual publicação em um índice público.
6. **Configuração:** documentar origem externa permitida, URLs dos provedores e Redis, limites e exposição de métricas. Não transportar configurações geradas de homologação, senhas ou certificados privados.

### Excluir da distribuição inicial da API

- Frontend Vue, node_modules, arquivos dist e pipeline de build do site.
- Pesquisa da candidate-1, coletores científicos, campanhas, snapshots, resultados reservados e grandes evidências históricas, salvo dependência operacional demonstrada e revisada.
- `.git` do oficial, ambientes virtuais, caches, `.env` locais, `.homolog`, `.historical-reports`, `.report-work`, entregas acadêmicas e vídeos.
- Documentos de planejamento sem relação com instalação, contrato ou operação do serviço.

Não excluir testes para esconder falhas. Testes exclusivamente científicos ficam no projeto geral, junto do código científico ao qual pertencem; as regressões do runtime precisam continuar no derivado.

## Proveniência e manutenção entre repositórios

Criar `UPSTREAM.md` com repositório oficial, SHA completo de extração, versão da política ativa e diferenças introduzidas no derivado. Registrar também hashes do contrato e regras quando o procedimento existente permitir comparação canônica reproduzível.

Decisões científicas permanecem no General-ClimaPrev. Correções operacionais podem nascer na API, mas sua incorporação ao projeto geral deve ser revisada e registrada. A candidate-1 somente entra em uma versão posterior da API se estiver qualificada; versionar essa mudança e preservar opção de retorno à política anterior.

Definir licença e atribuições antes de publicação aberta. Repositórios privados não substituem essa decisão e não devem perder o registro de autores/origem dos arquivos importados.

## Aceite técnico da primeira versão

- [ ] SHA de origem fixado, manifesto de extração e proveniência revisados.
- [ ] Instalação e build funcionam em clone limpo sem frontend ou arquivos do oficial.
- [ ] Compose autônomo, app/Redis saudáveis e configuração de exemplo suficiente para desenvolvimento.
- [ ] Contrato público preservado ou diferenças explicitamente aprovadas/documentadas.
- [ ] Reference-v1 preservada e resultados equivalentes em casos de regressão relevantes.
- [ ] Testes operacionais, Ruff, mypy, segurança e build passam no derivado.
- [ ] Cliente externo por HTTP/HTTPS e política CORS verificados; métricas internas não expostas indevidamente.
- [ ] Sem credenciais, dados reservados, artefatos pessoais ou dependências acidentais do monorepo.
- [ ] Licença/atribuições definidas para a distribuição pretendida.
- [ ] Primeiro push enviado ao destino correto e CI/Security do novo SHA aprovados.

Não transportar automaticamente a contagem de testes do monorepo como qualificação da API: registrar escopo e resultados próprios.

## Evolução comercial posterior

Após a extração estável, avaliar autenticação para clientes, gestão/revogação de credenciais, quotas por organização, versionamento e política de suporte, observabilidade e capacidade. A primeira entrega privada não implica serviço multiempresa pronto, SLA ou condições comerciais dos provedores já resolvidas.

## Próximo passo executável

Escolher o SHA qualificado de origem e preparar o manifesto de extração. Em seguida, usar checkout separado da API com a branch proposta, sem alterar a develop em andamento. A implementação do backend derivado e qualquer push são etapas futuras deste plano; nenhuma foi executada durante sua elaboração.
