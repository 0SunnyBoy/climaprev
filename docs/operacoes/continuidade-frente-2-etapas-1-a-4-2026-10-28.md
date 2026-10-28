# Continuidade da Frente 2 — Observações, Belém, piloto e comparação

Data: 28/10/2026. Escopo autorizado: etapas 1 a 4 da continuidade (desbloquear observações, reconciliar Belém, qualificar piloto e ampliar pareamento/comparação/cobertura). Sem ajuste da candidata, inferência estatística nova ou confirmação independente.

## Resultado das quatro etapas

| Etapa | Entrega | Estado e limite |
|---|---|---|
| 1 — Observações | Obtidos e validados os três CSVs públicos de 2026, até setembro, com temperatura instantânea declarada, umidade, chuva e rajada | Fonte oficial disponível; observações de outubro continuam sem acesso validado |
| 2 — Belém | Metadados do CSV 2026 coincidem com o catálogo atual | Reconciliado por versão da fonte; 2024 preservado, sem inferir deslocamento físico da estação |
| 3 — Piloto | Preflight pontual com cinco braços nos três locais, 15/15 concluídos; verificação explícita de prontidão observacional | Qualificação de coleta demonstrada pontualmente; piloto de 14 dias não ativado por falta de observações atuais e equivalência instrumental completa |
| 4 — Comparação | Parser experimental multivariável, pareamento por janela exata, comparação nos mesmos casos e cobertura com denominador planejado | Diagnóstico exploratório implementado; sem ganho real da candidata calculado ou intervalos de incerteza novos |

## Acesso ao INMET: diagnóstico e alternativa pública

O site oficial usa `POST /estacao/front/` com token reCAPTCHA. Na inspeção normal do navegador, o próprio componente mostrou: “Este site está excedendo a cota gratuita do reCAPTCHA Enterprise”. Não foi resolvido CAPTCHA, reproduzida chamada protegida ou contornado controle de acesso. O motivo específico dos HTTP 204 das rotas antigas não foi comprovado pelo servidor.

O [índice público de dados anuais](https://portal.inmet.gov.br/dadoshistoricos) disponibiliza 2026 até 30/09. O ZIP contém versões até agosto e até setembro; a seleção foi pela data de publicação anunciada, não pelo resultado meteorológico. Foram obtidos somente os CSVs das três estações por intervalos de bytes: aproximadamente 635 KB transferidos nas requisições de extração, em vez de baixar o ZIP completo de cerca de 137 MB. Houve consultas adicionais ao diretório para localizar e conferir a versão.

CRC do ZIP e SHA256 dos CSVs foram verificados. Arquivos brutos estão em `.report-work/front2-observations-2026-10-28/`, separados dos arquivos históricos e reservados existentes. São novas fontes observacionais de desenvolvimento, não confirmação independente.

Na janela publicada de 23/09 03 UTC a 30/09 03 UTC, as três estações tiveram cobertura de 100% nas variáveis importadas para o diagnóstico. Na janela recente de 21/10 03 UTC a 28/10 03 UTC, a cobertura desses arquivos é zero. Não reutilizar valores de setembro como medições de outubro. Integridade, cobertura e coincidência cadastral não certificam calibração, altura de sensor ou representatividade de grade.

## Reconciliação de Belém

- CSV de 2024: latitude -1,411228; longitude -48,439512.
- CSV de 2026 e catálogo atual: latitude -1,41111111; longitude -48,43944444.
- Regra: usar o ponto da versão observacional correspondente. O pareamento rejeita coordenadas incompatíveis; não houve aumento da tolerância ou alteração dos CSVs anteriores.

A discrepância histórica fica documentada, mas deixou de bloquear a preparação baseada no CSV de 2026, cujo cadastro coincide com o catálogo. Não há prova de mudança física de instrumento/local apenas pela diferença dos números.

## Qualificação dos cinco braços

Coleta pontual autorizada pelo runner com manifesto próprio, ledger/orçamento local, arquivo imutável e rodada 28/10 às 00 UTC para GFS/IFS/ICON. Não é o piloto recorrente nem uma campanha confirmatória.

- **GFS/IFS:** D+1/D+3/D+7 de chuva completos neste preflight nos três pontos.
- **ICON:** D+1/D+3 completos; D+7 incompleto nos três pontos.
- **MET Norway:** D+1 completo; D+3/D+7 sem soma diária elegível no agregador por intervalo exato nesta amostra. Isso não significa ausência total de previsão.
- **Baseline:** adaptador e política atuais arquivados nos três pontos; seleção/rodada automáticas permanecem desconhecidas. Não representa cache, avisos oficiais ou toda a rota pública.

O calendário do piloto continua desativado. O fingerprint agora inclui os módulos experimentais de observação e comparação multivariável; manifestos anteriores não devem ser adulterados para contornar divergência de versões. Antes de eventual ativação, gerar deliberadamente uma nova versão de calendário após as verificações necessárias, sem backfill de slots vencidos.

## Implementações

### Observações e prontidão

`experimental_observations.py` reutiliza o importador histórico sem alterá-lo e acrescenta campos opcionais do CSV: temperatura do ar e umidade horárias como amostras no endpoint declarado. Mantém chuva, rajada e extremos horários separados. Ausência de coluna ou sentinela não vira zero; umidade inválida, valores não finitos e colunas ambíguas são rejeitados.

Vento sustentado fica bloqueado até comprovar o período de média. As convenções temporais importadas não certificam a equivalência instrumental. `qualify_observation_window` mede cobertura na janela solicitada e compatibilidade cadastral; dados antigos não satisfazem uma janela recente.

### Pareamento e comparação

`experimental_multivariable.py` implementa:

- `pair_station_variable`: temperatura instantânea, umidade, rajada e contratos de extremos horários de temperatura; janelas exatas, unidades e exclusões explícitas, sem interpolação.
- `compare_variable_reports`: uma estação/alvo/período por comparação, métricas numéricas em casos comuns e denominador derivado do calendário esperado. Modelos precisam do mesmo slot UTC de meia hora; isso não prova igual idade de inicialização.
- Horas ausentes de todos os modelos permanecem no plano; contagens separadas de ausência e inelegibilidade.
- Verificação de fonte observacional comum, metadados, valores, duplicatas e coleta anterior ao dia-alvo.
- Dia civil calculado pelo fuso, incluindo 23/25 horas quando aplicável. Os pares horários não representam eventos independentes.

O normalizador de previsão atual fornece temperatura instantânea, não máxima/mínima horária. Os contratos de extrema não inventam essa previsão: ficam sem par elegível enquanto não houver informação equivalente. Chuva continua no comparador específico existente. Para estudar um horizonte, executar comparação do período/alvo correspondente; não interpretar uma média de períodos misturados como validação de todos os horizontes.

Os relatórios mantêm `scientific_approval=False` e `promotion_allowed=False`. Pareamento e pontuações exploratórias não autorizam promoção nem corrigem valores ausentes. Nenhuma precisão real foi medida com o preflight de outubro e as observações de setembro: são períodos diferentes.

## Verificação

**845 testes backend completos aprovados em 61,80 s**, warnings como erros, Redis de testes isolado. Mypy Linux em **88 módulos**, Ruff e verificação de whitespace aprovados. Novos cenários verificam colunas/sentinelas, chuva/rajada/unidades, temperatura versus extrema, casos comuns, omissões de todos os braços, mudança de horário, cronologia, metadados e dados antigos na janela recente.

Sem alteração do frontend ou da política pública de risco. Incremento local sem commit/push ou CI próprio.

## Próximos bloqueios e retomada

1. Obter fonte oficial com observações de outubro e validar unidades, cadência e qualidade. O caminho público anual validado atualmente termina em setembro; a interface recente depende do fluxo protegido do provedor.
2. Verificar detalhes instrumentais/altura/período de média antes de alegações científicas multivariáveis; preservar a distinção entre temperatura amostrada e extrema.
3. Atualizar deliberadamente os manifestos do piloto após estabilizar o pipeline e liberar somente o que estiver tecnicamente pronto. Sem ativação automática nesta rodada.
4. Na etapa posterior autorizada, implementar/calibrar incerteza e suporte antes de ajustar a candidata, congelar confirmação ou promover.

[Evidência da qualificação](../planejamento/reference-candidate-1/evidence/qualificacao-observacoes-piloto-2026-10-28.json) · [Allowlist observacional adicional](../planejamento/reference-candidate-1/fontes-observacionais-adicionais-2026-10-28.json) · [Benefícios esperados e condições](../planejamento/reference-candidate-1/beneficios-esperados-candidate-1.md).
