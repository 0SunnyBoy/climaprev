# Números emergenciais internacionais

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../../RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Status

Proposta de evolução futura. Este documento registra a ideia, os riscos e o
plano recomendado para adaptar a página **Números Emergenciais** ao país onde
a emergência está ocorrendo.

Nenhuma implementação internacional é considerada concluída enquanto os
números não forem revisados por fontes oficiais e submetidos a validação
manual.

## Objetivo

Permitir que o ClimaPrev apresente números de emergência compatíveis com o
país selecionado pelo usuário, sem substituir os canais oficiais nem assumir
que a localização do visitante é o local da emergência.

O sistema deve sempre permitir seleção manual, exibir a fonte dos dados e
usar um fallback seguro quando não houver informação verificada.

## Premissas de segurança

Números emergenciais são informação de alto impacto. Uma informação errada
pode atrasar o atendimento de uma pessoa em risco.

O ClimaPrev não deve:

- inferir um número apenas com base em um IP;
- substituir números confirmados por dados de uma API pública desconhecida;
- ocultar a fonte ou a data de verificação;
- inventar números para países sem dados validados;
- iniciar chamadas automaticamente;
- tratar a localização do usuário como o local da emergência sem confirmação.

Mesmo em regiões que possuem um número comum, podem existir números nacionais
ou regionais adicionais. Na União Europeia, por exemplo, o `112` funciona
junto com números nacionais em vários países, e não substitui universalmente
todas as opções locais. Consulte a [informação oficial da Comissão Europeia
sobre o 112](https://digital-strategy.ec.europa.eu/en/policies/112).

No Brasil, a Anatel registra códigos de emergência como `190` para a Polícia
Militar, `192` para o SAMU, `193` para o Corpo de Bombeiros e `199` para a
Defesa Civil. Consulte a [lista oficial de serviços de utilidade pública e
emergência da Anatel](https://www.gov.br/anatel/pt-br/regulado/acompanhamento-e-controle/servicos-de-utilidade-publica-e-de-emergencia-tridigitos).

## Estratégia de identificação do país

O sistema deve aplicar as fontes nesta ordem:

1. País selecionado manualmente pelo usuário.
2. País do local consultado na previsão.
3. País obtido a partir das coordenadas do usuário, somente após permissão
   explícita de geolocalização.
4. País estimado por IP, apenas como sugestão inicial e nunca como decisão
   definitiva.

O IP pode representar uma VPN, uma operadora, uma rede corporativa ou uma
localização aproximada. Por isso, ele não é suficiente para escolher
automaticamente um número de emergência.

O país do local consultado também pode ser diferente do país onde o usuário
está. Por exemplo, alguém no Brasil pode consultar a previsão de Tóquio. A
interface deve deixar essa diferença explícita e permitir a escolha entre:

- números do país do local consultado;
- números da localização atual do usuário;
- outro país escolhido manualmente.

## Experiência proposta

A página deve seguir este fluxo:

1. Exibir inicialmente os números do Brasil como fallback conhecido.
2. Mostrar um seletor de país com a opção atualmente aplicada.
3. Oferecer o botão **Usar minha localização**.
4. Solicitar a permissão de geolocalização somente após o usuário acionar o
   botão.
5. Detectar o país a partir das coordenadas, sem armazenar a localização além
   do necessário para a consulta.
6. Pedir confirmação antes de substituir os números exibidos.
7. Permitir a troca manual do país a qualquer momento.
8. Mostrar fonte, data de verificação e observações regionais.

Exemplo de aviso:

> Números exibidos para: Japão. Confirme se este é o local da emergência.

Quando não houver dados confirmados, a interface deve informar:

> Não temos números verificados para este país. Consulte os canais oficiais
> locais.

Os números devem continuar sendo links `tel:` acionados apenas por uma ação
explícita, como o botão **Ligar**.

## Modelo de dados

O primeiro modelo pode ser mantido no frontend, em um arquivo versionado:

```ts
type EmergencyCountry = {
  countryCode: string
  countryName: string
  locale: string
  verifiedAt: string
  sources: string[]
  services: EmergencyService[]
}

type EmergencyService = {
  id: string
  name: string
  number: string
  description: string
  regions?: string[]
  availableLanguages?: string[]
}
```

Exemplo de registro:

```ts
{
  countryCode: "BR",
  countryName: "Brasil",
  locale: "pt-BR",
  verifiedAt: "2026-09-24",
  sources: ["https://www.gov.br/anatel/..."],
  services: [
    {
      id: "police",
      name: "Polícia Militar",
      number: "190",
      description: "Atende ocorrências de segurança pública."
    }
  ]
}
```

O arquivo pode ficar inicialmente em:

```text
frontend/src/data/emergencyNumbers.ts
```

## Fonte dos dados

Cada país deve ser incluído somente após uma revisão que registre:

- fonte oficial do governo, órgão de telecomunicações, polícia, bombeiros,
  saúde ou defesa civil;
- data da verificação;
- país, região ou província aplicável;
- descrição do serviço;
- observações sobre disponibilidade, idioma ou restrições locais;
- ao menos uma fonte alternativa quando a estrutura do país for complexa.

A base deve ser atualizada por pull request. Um país com dados vencidos deve
ser marcado para revisão, e não atualizado automaticamente por uma fonte não
confiável.

## Evolução futura da API

Depois que a base inicial estiver validada, o backend pode expor:

```text
GET /api/v1/emergency-services?country=BR&region=PA&language=pt-BR
```

A API deve retornar os serviços, o país aplicado, a data de verificação, as
fontes e eventuais ressalvas regionais. Redis pode armazenar o resultado por
um período curto, mas não deve ser tratado como fonte primária dos números.

O frontend deve manter um fallback local para continuar exibindo uma
orientação segura quando a API estiver indisponível.

## Validações obrigatórias

Antes de publicar um novo país:

1. Confirmar os números em fontes oficiais.
2. Revisar manualmente a descrição de cada serviço.
3. Confirmar o formato do número para `tel:`.
4. Verificar se o número é nacional ou depende de uma região.
5. Registrar a data e as URLs das fontes.
6. Criar teste para impedir país sem serviço primário ou sem fonte.
7. Validar os textos em português e inglês.
8. Testar fallback para Brasil e país sem cadastro.
9. Testar seleção manual, geolocalização negada e localização indisponível.
10. Revisar a interface em desktop, celular, teclado e leitor de tela.

## Plano de implementação

### Etapa 1 — Base segura

- Manter o Brasil como fallback.
- Criar o seletor manual de país.
- Mover os números atuais para uma estrutura tipada.
- Adicionar fonte e data de verificação.
- Implementar testes de integridade dos registros.

### Etapa 2 — País do local consultado

- Usar o país retornado pelo serviço de geocodificação.
- Exibir uma sugestão, sem trocar automaticamente os números.
- Pedir confirmação antes da alteração.
- Permitir retornar aos números do Brasil.

### Etapa 3 — Localização atual

- Adicionar o botão de geolocalização.
- Solicitar permissão somente após interação do usuário.
- Fazer reverse geocoding para obter o país.
- Evitar persistir coordenadas precisas.
- Informar quando a localização não puder ser determinada.

### Etapa 4 — API própria

- Centralizar a base validada no backend.
- Adicionar cache e versionamento da resposta.
- Monitorar registros vencidos.
- Manter fallback local no frontend.

## Recomendação

O caminho recomendado é começar pela Etapa 1. Ela entrega adaptação
internacional controlada sem depender de IP, sem solicitar localização
automaticamente e sem colocar uma API de terceiros no caminho crítico de uma
emergência.

A geolocalização e a detecção por IP devem ser complementares. A seleção
manual, as fontes oficiais, a data de verificação e o fallback seguro devem
continuar existindo mesmo depois da automatização.
