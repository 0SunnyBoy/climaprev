# Horizonte público de 14 dias, consultas de até sete — 30/10/2026

## Comportamento

Implementada a janela pública de **hoje UTC até hoje UTC +13**, inclusive. Cada consulta GET/POST continua limitada a **um a sete dias consecutivos**. A data final omitida continua equivalente à inicial. São aceitas consultas somente na segunda semana, por exemplo D+7 a D+13; oito dias, datas passadas e D+14 são rejeitados antes de chamar o serviço.

O formulário acompanha o mesmo corte UTC, atualiza limites ao mudar o dia ou retornar ao foco e limita a data final ao menor valor entre início+6 e o fim da janela de 14 dias. Textos em português/inglês e descrições OpenAPI foram atualizados. Há orientação para rever previsões da segunda semana mais perto da data, sem inventar probabilidades de confiança. Os dias meteorológicos continuam agregados no fuso da localidade, conforme o contrato existente.

## Provedor e qualidade

O adaptador Open-Meteo já envia `start_date`/`end_date`; não foi alterado nem passou a buscar 14 dias para toda consulta. A [documentação oficial](https://open-meteo.com/en/docs) permite intervalos de previsão dentro de até 16 dias. O produto mantém 14, com no máximo sete datas por requisição.

Verificação real em Belém: intervalo de sete dias da segunda semana retornado completo, sem campos ausentes nessa amostra. A execução ocorreu na noite local de 30/10, já em 31/10 UTC; as datas solicitadas foram 07–13/11. Evidência com horário UTC em `docs/operacoes/evidence/horizonte-14-7-2026-10-30.json`. Essa consulta testa disponibilidade e normalização em um ponto, não precisão ou cobertura universal. Limites e ausência de campos continuam tratados pelo fluxo de qualidade existente; não houve preenchimento de medições ausentes.

Política reference-v1, limiares, prazos, cache por período e formato da resposta permanecem. A descrição do contrato mudou: novo SHA256 canônico OpenAPI `474199bf4155eec9bde52b4343e0aaed12888bee7315f9e87460b48efaac62fe`. A lista de valores públicos conhecidos do Gitleaks inclui somente esse hash exato adicional; regras e credenciais sintéticas continuam verificadas.

## Piloto científico preservado

Nenhum módulo do pipeline congelado da coleta foi modificado; o calendário ativo foi validado novamente. O coletor experimental da baseline continua preservando o controle de sete datas originalmente congelado. Sua mensagem histórica de limite público refere-se a esse contrato do controle, não à nova elegibilidade da rota pública.

D+7 passa a ser consultável na API pública, mas não é acrescentado retroativamente às capturas da baseline do piloto. A ausência desse controle em D+7 continua explícita no estudo existente; comparar com a versão pública ampliada requer novo desenho/registro. Não alterar evidências históricas ou afirmar ganho da candidate-1 por ampliar datas. A automação, sua cota e as reposições seguem como autorizadas.

## Qualificação

- Backend Linux: **1.170 testes aprovados**, warnings como erros; mypy em **99 módulos**.
- Frontend Node.js 22: **60 testes**, lint e build aprovados; instalação pelo lockfile sem vulnerabilidades reportadas.
- Testes cobrem UTC, virada do ano/meia-noite, primeira/segunda semana, limite de sete dias, fronteira D+13/D+14 e propagação GET/POST.
- Gate de navegador HTTPS ajustado para conferir a janela de 14 datas. Conferir CI/Security do commit publicado para qualificação remota própria.

Esta entrega conclui o incremento funcional 14/7. Validação científica da candidata, equivalência instrumental real, acessibilidade auditiva, distribuição/comercial e hospedagem continuam pendências independentes. Janela 16/8 e previsões sazonais não foram implementadas.
