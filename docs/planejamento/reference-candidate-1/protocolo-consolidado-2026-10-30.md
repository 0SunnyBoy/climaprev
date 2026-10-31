# Protocolo consolidado — preparação técnica de 30/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Estado e escopo

Direção e parâmetros prospectivos registrados por delegação do usuário. Este documento concilia a frente 2 com os contratos executáveis recebidos da develop2. Não declara superioridade, independência demonstrada, congelamento confirmatório ou autorização de promoção. Os protocolos anteriores permanecem preservados.

Artefatos: `protocolo-consolidado-2026-10-30.json`, `criterios-consolidados-2026-10-30.json`, `particoes-temporais-2026-10-30.json` e `evidence/prontidao-piloto-2026-10-30.json`. O envelope do protocolo foi validado pelo contrato recebido. O JSON de critérios registra as condições que ainda dependem de dados.

## Objetivo e população

Objetivo primário: comparar uma futura candidata congelada com a baseline operacional em chuva diária D+1. Comparar as previsões disponíveis no mesmo slot de decisão; isso não comprova mesma idade de rodada. Baseline automática mantém modelo/rodada desconhecidos. Chuva D+3/D+7, demais modelos e variáveis permanecem exploratórios. Sem baseline pública D+7 não haverá alegação de ganho contra a v1 nesse horizonte.

Estações iniciais: A201 Belém, A001 Brasília e A801 Porto Alegre. Catálogo oficial reconsultado em 30/10 marca as três como operantes; coordenadas dos CSVs públicos de 2026 coincidem com o catálogo dentro da tolerância existente. Isso não certifica instrumento, altura, calibração ou qualidade recente. Representatividade estação/grade continua uma limitação.

Calendário do piloto: 14 slots de 31/10 a 13/11/2026 às 18 UTC, equivalentes a 15h de Brasília. Cinco braços por estação: baseline operacional, GFS, IFS, ICON e MET Norway. São 210 jobs e 630 alvos de chuva, considerando D+1/D+3/D+7; não são 630 observações já existentes. Os alvos vão de 01 a 20/11. Janela de execução de 30 minutos e orçamento local de 30 chamadas por provedor/dia, compartilhado pelo ledger. Sem rotina permanente, retentativas silenciosas ou backfill.

O calendário executável novo usa o protocolo e o runner recebidos, desativado e sem registros E1/E2/E3 criados. Usa disponibilidade no slot, sem fixar inicialização: identidades desconhecidas continuam desconhecidas. O calendário antigo com solicitações 00 UTC continua histórico; não misturar sua interpretação de antecedência com o novo desenho. Uma comparação secundária controlada por rodada exige protocolo próprio e evidência da inicialização.

## Critérios e estatística

- Meta direcional: redução pontual de pelo menos 5% no MAE, acompanhada de intervalo pareado para a diferença absoluta de MAE com limite superior abaixo de zero. Isso não comprova um limite inferior de confiança de 5% de ganho.
- Cobertura mínima prospectiva de 90% por estação e objetivo primário, sempre contra o calendário planejado. É uma escolha operacional, não uma garantia de poder estatístico.
- Reportar ganho absoluto em mm/dia. A margem de 0,5 mm continua apenas sensibilidade; não foi transformada em mínimo físico validado.
- Proteção de extremos: chuva diária de pelo menos 50 mm como limiar diagnóstico da política atual. Exigir proteção de detecção e razão de falsos alarmes, sem tolerância automática à piora. Essa razão é falsos alarmes/eventos previstos.
- Confiança reportada de 95%; largura máxima prospectiva de 0,10 nos intervalos de diferenças das taxas, condicionada à validade do método e ao suporte. Um evento é somente piso de computabilidade, não amostra suficiente. O mínimo efetivo de eventos independentes continua sem valor fabricado.
- Reamostragem pareada por blocos de datas, agrupando estações. Examinar 7/14/28 dias em desenvolvimento. Tamanho final e validade do procedimento devem ser fixados antes da confirmação, sem escolher o bloco pelo resultado reservado.
- Ausência de eventos, denominadores nulos, intervalos degenerados, lacunas ou suporte inadequado produzem resultado inconclusivo. A rotina de percentis existente permanece exploratória até a qualificação do método.

Plano de multiplicidade: uma única candidata e um único objetivo primário pré-fixados, com todos os guardas de extremos necessários para qualquer promoção. Não selecionar o melhor modelo, estação, horizonte ou bloco usando o teste confirmatório. Comparações secundárias não produzirão alegações formais de superioridade. Os intervalos atuais são marginais, sem correção simultânea; a implementação não sustenta alegações de proteção conjunta com confiança de 95%. A análise conjunta e o suporte precisam de revisão metodológica antes da confirmação. Nenhuma fórmula de correção foi aplicada sem essa revisão.

Referências metodológicas: [recomendações WGNE para verificação de precipitação](https://www.cawcr.gov.au/projects/verification/WGNE/QPF_verif_recomm.pdf) e [pesquisa sobre dependência nas comparações de previsões](https://journals.ametsoc.org/doi/pdf/10.1175/MWR-D-17-0295.1). Fundamentam o cuidado com incerteza e dependência; não validam os números operacionais específicos deste projeto.

## Partições e congelamento

O novo piloto tem alvos D+7 até 20/11. Por isso, o planejamento de desenvolvimento termina em 20/11 e a seleção foi deslocada para 05–31/12/2026. Primeira emissão D+7 da seleção em 28/11, com limite de congelamento do conjunto de alternativas em 27/11 às 23 UTC. Mantém-se a referência condicional de confirmação de 15/01/2027 a 14/01/2028 e congelamento final em 07/01/2027 às 23 UTC, anterior à primeira emissão D+7 de 08/01.

Embargo mínimo de sete dias também entre emissões e partições. Verificação aritmética aprovada; não equivale a independência meteorológica comprovada ou congelamento efetuado. Só as fontes de desenvolvimento já autorizadas podem ser usadas. Datas abrangentes não autorizam abrir fontes desconhecidas ou reservas. Se perder um marco, invalidar e registrar novo calendário antes dos resultados, sem prolongar o teste em função do desempenho.

## Fontes e equivalência

O estudo mantém GFS/IFS/ICON explícitos pela Open-Meteo, baseline operacional como controle e MET Norway como braço secundário. São modelos adicionais e dois provedores de acesso; não são duas novas APIs independentes adicionadas ao produto. MET global deriva de ECMWF e não deve ser contado como confirmação independente de IFS. Nenhuma combinação foi selecionada por desempenho.

Revisão de uso: a [API gratuita Open-Meteo](https://open-meteo.com/en/terms) permanece restrita ao uso não comercial; licença dos dados e acesso ao serviço são condições diferentes. O piloto acadêmico/público usa esse enquadramento. Oferta empresarial, publicidade ou uso comercial exigem enquadramento próprio antes de ativação comercial. MET exige [identificação, uso responsável e atribuições aplicáveis](https://api.met.no/doc/TermsOfService); seu [modelo global e ausência de histórico global pela API](https://api.met.no/doc/locationforecast/datamodel) limitam independência e retrospectiva. Não houve contratação, ingestão direta ECMWF ou implantação empresarial.

Contratos observacionais revalidados no [glossário oficial INMET](https://portal.inmet.gov.br/glossario/nublado): temperatura horária automática é média anterior; vento horário é média dos últimos dez minutos; rajada é máxima anterior; umidade horária não tem agregação suficientemente explícita para pareamento instantâneo. Chuva é o alvo primário elegível sob soma e cobertura exatas. Rajadas são secundárias sob contrato próprio. Não derivar médias/extremos observados de amostras instantâneas nem tratar compatibilidade temporal como certificação instrumental.

## Prontidão e execução

Verificação de 30/10: endpoints recentes retornaram HTTP 204 nas três estações; o [índice anual público](https://portal.inmet.gov.br/dadoshistoricos) continua até 30/09/2026. CSVs conhecidos não cobrem a janela concluída de 23 a 29/10: cobertura recente de chuva zero. O preflight existente é de 28/10; foi reavaliado offline com o pipeline combinado e é antigo para nova prontidão.

O verificador agora exige relógios válidos e captura de previsão com no máximo 24 horas. Esse prazo é uma regra operacional de preparação, não equivalência de rodada ou norma científica. Nenhuma nova previsão foi coletada para repetir um preflight enquanto a observação permanece bloqueada. Não houve acesso a resultados reservados.

Resultado: piloto não pronto, sem ativação. Para retomar: obter fonte recente legítima, verificar cobertura e metadados, refazer preflight pontual atual, regenerar calendário no runtime de execução com código/versões conferidos e repetir a qualificação. Hashes atuais refletem o runtime local e não devem ser reescritos para contornar divergência. Depois, registrar o aceite de execução aplicável e decidir a ativação. A autorização desta rodada termina na prontidão, sem iniciar campanha longa, fitting ou promoção.
