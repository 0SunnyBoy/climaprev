# Análise de licenciamento e preparação para publicação — ClimaPrev

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 16/10/2026. Repositório: [0SunnyBoy/climaprev](https://github.com/0SunnyBoy/climaprev).

## Conclusão

Há caminhos viáveis para publicar o código próprio sob Apache-2.0, MIT, MPL-2.0, GPL-3.0 ou AGPL-3.0. A análise preliminar das dependências não identificou uma obrigação de adotar copyleft para todo o ClimaPrev. A compatibilidade final depende dos componentes efetivamente distribuídos, de seus avisos e da origem das contribuições.

**Recomendação para discussão entre os quatro contribuintes: Apache-2.0 se o objetivo for facilitar adoção e reutilização, inclusive comercial e em produtos fechados; AGPL-3.0 se o objetivo for exigir acesso ao código correspondente de versões modificadas oferecidas pela rede.** MPL-2.0 é uma alternativa intermediária para compartilhamento de arquivos modificados quando distribuídos.

Não foi aplicada uma licença nem alterada a visibilidade do repositório. Este documento é uma análise técnica e informativa; não confirma titularidade jurídica nem substitui a avaliação de contratos específicos.

## Escopo e evidências

- O conector GitHub confirmou visibilidade `private`, branch padrão `main` e três branches: `main`, `develop` e `old-develop`.
- A árvore remota completa de `main`, commit `7f1bb3bc91c774d2c68237d89e5968d79314f823`, contém 249 arquivos. Não foram encontrados arquivos de licença, `NOTICE`, `CONTRIBUTING.md` ou `SECURITY.md` nessa árvore.
- O checkout local está em `develop`, commit `23bf4cee997bc825e76028f99eefd6160f699ee5`, correspondente ao head remoto consultado. Há modificações e arquivos locais não commitados, que não devem ser confundidos com conteúdo já publicado no GitHub.
- Foram examinados metadados do projeto, lockfile JavaScript, metadados das distribuições Python instaladas, Dockerfiles, Compose, configuração de segurança e componentes da interface.
- O histórico local apresenta cinco nomes de autoria. O responsável informou que existem quatro contribuintes; nomes de commit podem representar aliases e não comprovam quantidade de pessoas ou titularidade.
- Esta análise não executou um novo scanner de segredos, não auditou todos os blobs históricos e não validou todas as licenças de pacotes do sistema operacional nas imagens Docker.

## Opções para o código próprio

| Licença | Uso comercial | Versões fechadas | Principal obrigação | Quando faz sentido |
| --- | --- | --- | --- | --- |
| MIT | Permitido | Permitidas | Preservar aviso de copyright e licença nas cópias ou porções substanciais | Simplicidade e ampla reutilização |
| Apache-2.0 | Permitido | Permitidas | Preservar licença e avisos aplicáveis, indicar arquivos alterados e transportar atribuições de NOTICE quando aplicável | Reutilização com concessão expressa de patentes dos contribuintes |
| MPL-2.0 | Permitido | Possíveis para arquivos separados | Disponibilizar sob MPL os fontes dos arquivos cobertos, incluindo modificações, aos destinatários da distribuição | Compartilhamento das melhorias nos arquivos existentes, permitindo integração proprietária |
| GPL-3.0 | Permitido | Não para obras derivadas distribuídas cobertas pela GPL | Disponibilizar código correspondente aos destinatários e preservar a licença na distribuição | Manter derivados distribuídos livres |
| AGPL-3.0 | Permitido | Não para derivados cobertos nos casos abrangidos | Obrigações da GPL e oferta do código correspondente da versão modificada aos usuários que interagem com ela pela rede | Aplicações web e APIs em que o compartilhamento das modificações é prioritário |

A GPL não cria, por simples execução do backend em um servidor, a obrigação de oferecer aos usuários remotos o fonte das modificações. A AGPL trata especificamente desse cenário. Isso não significa obrigação de abrir todo sistema independente que consuma a API: o alcance depende da relação entre os programas. No frontend, entregar JavaScript compilado ao navegador é uma distribuição relevante para a análise de copyleft.

Apache-2.0 não exige que um terceiro entregue suas melhorias ao projeto. Sua concessão de patentes é limitada às reivindicações licenciáveis dos contribuintes abrangidas pelo texto, e não uma garantia contra patentes de qualquer terceiro. MIT também não exige retorno das alterações e não contém concessão expressa equivalente.

BSD-3-Clause também é uma opção permissiva, mas não apresenta uma vantagem clara sobre MIT ou Apache-2.0 para os objetivos informados. Licenciamento duplo, por exemplo AGPL com alternativa comercial, é possível se houver direitos suficientes sobre todas as contribuições; não deve ser presumido pela propriedade da conta GitHub.

Fontes: [MIT](https://opensource.org/license/mit), [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), [MPL — FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/), [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/), [AGPL-3.0](https://choosealicense.com/licenses/agpl-3.0/), [por que usar Affero GPL](https://www.gnu.org/licenses/why-affero-gpl.html).

## Dependências e dados: obrigações separadas

### Bibliotecas

O `frontend/package-lock.json` local declara 310 entradas de pacotes: 257 MIT, 16 Apache-2.0, 15 ISC, 10 BSD-2-Clause, 7 BlueOak-1.0.0, 3 BSD-3-Clause, 1 MIT-0 e 1 Python-2.0. Não foram encontrados identificadores de licenças ausentes, GPL, AGPL ou MPL nesse inventário. São metadados declarados; não equivalem à inspeção jurídica de cada arquivo. Vue está declarado sob MIT e TypeScript sob Apache-2.0.

Nos metadados Python instalados, FastAPI, Pydantic, redis-py e hiredis declaram MIT; Uvicorn, HTTPX e Starlette declaram BSD-3-Clause. `certifi` declara MPL-2.0 e `pathspec`, usado pelas ferramentas de desenvolvimento, declara MPL-2.0. Isso exige preservar suas condições quando incluídos em uma distribuição; não obriga, por si só, a licenciar todo o código próprio sob MPL. As dependências mantêm suas próprias licenças.

Para distribuição de wheels, frontend compilado ou imagens, preparar um inventário de terceiros e conservar os textos e avisos necessários. Um arquivo de inventário com nomes e links não substitui textos que precisem acompanhar a distribuição. Revisar separadamente as imagens de runtime, desenvolvimento e carga, pois incluem componentes diferentes. Referência para o alcance por arquivos: [Mozilla](https://www.mozilla.org/en-US/MPL/2.0/FAQ/).

### Redis servidor

O Compose fixa `redis:7-alpine` pelo digest `sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf`. A versão menor correspondente ao digest não foi resolvida nesta análise. Portanto, não é correto atribuir BSD a essa imagem apenas porque o tag começa com 7.

Segundo o Redis, versões até 7.2 usam BSD-3-Clause; 7.4 usa RSALv2 ou SSPLv1; a partir de 8 há também a opção AGPLv3. O servidor Redis e o cliente Python redis-py são componentes diferentes. Consumir Redis como serviço separado não determina automaticamente a licença do código ClimaPrev.

Antes de distribuir a stack, identificar a versão exata e suas condições. Caso vocês desejem uma stack com datastore sob licença permissiva, avaliar Valkey, sob BSD, como alternativa com testes de compatibilidade. Não recomendo mudar para uma versão antiga apenas por licença, ignorando manutenção e segurança. Fontes: [licenças Redis](https://redis.io/legal/licenses/), [Valkey](https://valkey.io/).

### Open-Meteo

Há três assuntos distintos: licença do código próprio, licença dos dados e termos de acesso à API hospedada.

- Os dados da API são oferecidos sob CC BY 4.0: atribuir a fonte, ligar à licença e indicar modificações aplicáveis. A página do provedor pede um link próximo de onde seus dados são exibidos.
- O acesso gratuito à API é limitado a uso não comercial e limites de requisições. Aplicações com anúncios ou assinaturas são exemplos de uso comercial nos termos atuais. O projeto ser open source não torna automaticamente sua operação não comercial.
- O código do servidor Open-Meteo é AGPL, mas nesta implementação o ClimaPrev faz requisições HTTP à API. Essa integração, por si só, não impõe AGPL ao código cliente.

A interface examinada mostra o identificador da fonte em `frontend/src/components/ForecastResult.vue:24`, mas a busca no frontend não encontrou link para Open-Meteo ou menção à licença. Ajustar a atribuição visível e documentar as condições operacionais. A geocodificação também utiliza dados GeoNames, cuja atribuição deve ser contemplada conforme a licença aplicável.

Fontes: [licença e atribuição Open-Meteo](https://open-meteo.com/en/licence), [termos de acesso](https://open-meteo.com/en/terms), [origem da geocodificação](https://open-meteo.com/en/docs/geocoding-api).

### INMET e referências externas

O projeto consulta alertas INMET e há ferramentas locais para importar observações. As páginas oficiais consultadas não forneceram uma licença específica suficiente para concluir sobre toda redistribuição desses materiais. Documentar origem, endpoint, data de coleta e condições aplicáveis antes de publicar datasets ou arquivos de terceiros. Não atribuir automaticamente a esses dados a licença escolhida para o código. Referência consultada: [dados históricos INMET](https://portal.inmet.gov.br/dadoshistoricos).

`docs/arquitetura/analise-referencias-sigfas.md` registra aproveitamento de estruturas de documentos de outro projeto. Isso não demonstra infração, mas exige esclarecer se houve reprodução de conteúdo protegido, quais são seus titulares e quais permissões existem. O mesmo vale para imagens e qualquer material criado fora do ClimaPrev.

## Os quatro contribuintes

Antes da primeira publicação licenciada, registrar a concordância dos quatro titulares, ou de quem legitimamente represente seus direitos. Confirmar se as contribuições pertencem aos próprios autores ou estão sujeitas a contratos com empresas ou instituições. Ser administrador do repositório não transfere os direitos das contribuições.

Uma forma prática é cada titular registrar, em um issue ou documento de aprovação, sua autorização para distribuir suas contribuições existentes sob a licença escolhida, identificando projeto e versão/commit abrangidos, e confirmar a origem autorizada dos materiais. Este é um roteiro de registro, não um instrumento de cessão de direitos.

Para novas contribuições, criar `CONTRIBUTING.md` explicando que elas entram sob a licença do projeto. O DCO pode registrar a declaração de origem e direito de contribuir por meio de sign-off; não transfere copyright e não substitui a autorização para licenciar contribuições históricas. Um CLA mais amplo faz sentido se houver plano concreto de licenciamento duplo ou necessidade de direitos adicionais. Fontes: [guia jurídico de código aberto](https://opensource.guide/legal/), [DCO](https://developercertificate.org/).

## Preparação antes de mudar a visibilidade

1. Definir o objetivo entre os quatro contribuintes: ampla reutilização, compartilhamento por arquivo ou reciprocidade em serviços web. Registrar a autorização dos titulares sobre a licença escolhida.
2. Criar `LICENSE` com o texto oficial sem restrições personalizadas incompatíveis. Declarar escopo, identificação dos titulares e licença nos metadados Python e Node e no README. `private: true` no package.json apenas evita publicação acidental no npm; não define a visibilidade GitHub nem impede código aberto.
3. Criar inventário e avisos de terceiros; assegurar inclusão nos artefatos distribuídos. Se necessário, documentação própria pode ter licença separada, como CC BY 4.0, com escopo explícito; Creative Commons recomenda licenças específicas de software para código.
4. Corrigir a atribuição Open-Meteo, contemplar GeoNames e esclarecer termos do INMET e versão/licença exata do servidor Redis.
5. Revisar todo o histórico e todas as branches que permanecerão públicas, inclusive `old-develop`, além de releases, anexos e logs de Actions acessíveis. Há workflow de Gitleaks com histórico completo e política de exclusão de segredos, mas sua existência não comprova um resultado recente limpo. Conferir a execução e revisar eventuais credenciais históricas, materiais pessoais e informações de terceiros antes da exposição.
6. Criar `CONTRIBUTING.md` e `SECURITY.md`, definir revisão de pull requests e proteção da branch principal. A API consultada retornou `protected: false` nas três branches; regras de repositório adicionais não foram auditadas. Revisar a configuração efetiva de proteção antes de abrir contribuições.
7. Preservar o aviso funcional já existente sobre estimativas meteorológicas e alertas oficiais. Cláusulas de ausência de garantia da licença não substituem comunicação correta sobre as limitações do produto.

Tornar o repositório público não o torna automaticamente open source: sem licença, permanecem os direitos reservados, com permissões específicas de visualização/fork previstas pelo GitHub. Licenças open source permitem uso comercial; acrescentar uma proibição de uso comercial altera essa classificação. Licenciar código também não concede automaticamente direitos de marca. Fontes: [GitHub — licenciamento](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository), [definição OSI](https://opensource.org/osd), [Creative Commons — software](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software).

As permissões concedidas sobre versões já distribuídas sob uma licença aberta não são simplesmente desfeitas ao tornar o repositório privado ou mudar a licença de versões futuras. Escolher agora considerando o objetivo de longo prazo e os direitos sobre as contribuições.
