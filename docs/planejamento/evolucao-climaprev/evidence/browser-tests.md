# Roteiro Browser reproduzível — B01–B10

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../../projeto/STATE.md) · [RDP](../../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

> Evidência histórica do frontend anterior à migração Vue/TypeScript. Os
> exemplos que importam `frontend/api.js` representam o contrato de teste da
> implementação antiga e não devem ser executados contra o frontend atual.
> Para o estado atual, use `tests/docker/check_frontend_browser.py` e
> `tests/docker/check_frontend_security.py`.

Os blocos abaixo são as fontes exatas dos scripts executados em Chrome 152
visível com Playwright disponível no host. Eles usam respostas sintéticas
interceptadas, sem chamar o provedor público. TLS é verificado separadamente
na entrada real de homologação. Não há instalação npm no aplicativo.

Para reproduzir neste host, primeiro extraia os scripts para `/tmp`:

```python
from pathlib import Path
import re
source = Path("docs/planejamento/evolucao-climaprev/evidence/browser-tests.md").read_text()
for name, body in re.findall(r"## Arquivo: ([\w.-]+)\n\n```(?:javascript|python)\n(.*?)\n```", source, re.S):
    Path("/tmp", name).write_text(body + "\n")
```

Executar a extração com Python 3 na raiz do repositório. Os requires dos scripts
usam a instalação Playwright deste host e o Chrome em `/usr/bin/google-chrome`;
em outro host, ajuste esses caminhos à instalação local equivalente.
URLs são configuráveis por `CLIMAPREV_UI_URL` e `CLIMAPREV_TLS_URL`.
`CLIMAPREV_CA_PATH` aponta somente ao certificado público da CA.

```bash
# Aplicação HTTP temporária, se ainda não estiver executando:
docker compose run -d --name climaprev-ui-browser -p 127.0.0.1:18000:8000 -v "$PWD/src:/app/src:ro" app
# Não execute novamente com o mesmo nome se o contêiner já existir.
node /tmp/playwright-test-climaprev-t21.js
node /tmp/playwright-test-climaprev-t22.js
node /tmp/playwright-test-climaprev-t23.js
node /tmp/playwright-test-climaprev-t24.js
node /tmp/playwright-test-climaprev-t25.js
node /tmp/playwright-test-climaprev-tls.js
docker compose --env-file .homolog/compose.env -f docker-compose.homolog.yml exec -T app python < /tmp/climaprev-check-runtime-assets.py
```

O teste TLS primeiro comprova a rejeição da CA, inicializa o banco de
certificados de um perfil Chrome descartável e insere apenas a CA pública
como confiança TLS. Reabre o mesmo perfil e verifica HTTPS sem flags de bypass.
O perfil é removido no finally; nenhum trust store global muda. A representação
SQLite/protobuf foi verificada para Chrome 152; não é um importador genérico
para todas as versões. A prova usa fetch do navegador, pois o cliente HTTP
Node de Playwright tem um trust store separado do perfil Chrome.

O teste de teclado preenche o controle de data nativo do Chrome deste host,
que usa segmentos mês/dia/ano. O valor enviado e assertado é ISO; outros
navegadores podem apresentar outra ordem. Viewports assertadas são 360/1280;
a imagem de página inteira pode ter 345/1265 px de conteúdo por descontar a
barra de rolagem vertical. Não há overflow horizontal.

| Caso | Script / cobertura |
| --- | --- |
| B01 | T21/T22: cidade, coordenadas, allowlist, trim, data final vazia |
| B02 | T25: texto vazio/espaços, par incompleto, limites de datas/coordenadas |
| B03 | T22/T23: parâmetro de unidade e valores C/F; demais unidades preservadas |
| B04 | T23: local, fuso, datas, fonte, coleta, dias, risco, aviso |
| B05 | T23: parcial/indisponível/stale/null, opcional ausente e risco alto parcial |
| B06 | T23: estados oficiais distintos e conteúdo de alerta |
| B07 | T24: HTTP 404/422/502/503/500, rede, JSON malformado, foco/contexto |
| B08 | T24: header válido/inválido/ausente, corpo inválido, deadline/timer atrasado |
| B09 | T23/T24: marcação inerte, resposta antiga ignorada e HTTP abortado |
| B10 | T25: teclado, labels, foco, status, detalhes e layout 360/1280 |

Contagem operacional: T21=2, T22=7, T23=12, T24=16 e T25=10 cenários,
47 verificações agrupadas nos 5 scripts (não são testes pytest). TLS acrescenta
uma prova de rejeição/confiança e runtime uma prova de empacotamento.
As contagens incluem cenários de privacidade/foco no mesmo fluxo; B01–B10
continua sendo a matriz normativa. Nenhuma captura representa dados reais.

## Arquivo: climaprev-browser-fixture.cjs

```javascript
exports.fixture = (overrides = {}) => ({
 request_id:'browser-fixture-123', location:{name:'Belém, Pará',latitude:-1.4558,longitude:-48.4902,timezone:'America/Belem',source:'synthetic-geocoding'},
 period:{start_date:'2026-09-13',end_date:'2026-09-14'}, temperature_unit:'celsius',
 days: ['2026-09-13','2026-09-14'].map((date, i) => ({date,temperature_min:24+i,temperature_max:32+i,temperature_mean:28+i,humidity_mean_pct:82,precipitation_sum_mm:18,precipitation_probability_max_pct:75,precipitation_max_hourly_mm:8,wind_max_kmh:16,wind_gust_max_kmh:28,weather_code:3})),
 forecast_risk:{level:'moderate',method:'forecast_heuristic',policy_version:'reference-v1',conditions:[{type:'heavy_rain_proxy',severity:'moderate',value:18,unit:'mm/day',reason:'Chuva prevista requer atenção; não é um alerta oficial.'}]},
 official_alerts:{status:'not_configured',items:[]},data_quality:{is_stale:false,missing_fields:[],completeness:'complete'},source:{provider:'Open-Meteo (fixture local)',fetched_at:'2026-09-13T12:00:00Z'},
 disclaimer:'Estimativa baseada em previsão. Não substitui alertas oficiais nem uma avaliação local.',...overrides,
});
```

## Arquivo: playwright-test-climaprev-t21.js

```javascript
const { chromium, expect } = require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const TARGET_URL = process.env.CLIMAPREV_UI_URL || 'http://127.0.0.1:18000';
(async () => {
 const browser = await chromium.launch({headless:false, executablePath:'/usr/bin/google-chrome'});
 try {
  const page = await browser.newPage();
  await page.route('**/api/v1/risk?*', route => route.fulfill({json:{}}));
  await page.goto(TARGET_URL);
  await page.screenshot({path:'/tmp/climaprev-t21-desktop.png',fullPage:true});
  await expect(page.getByRole('heading',{name:'Sua consulta'})).toBeVisible();
  await expect(page.getByLabel('Latitude',{exact:true})).toBeHidden();
  await page.getByLabel('Cidade',{exact:true}).fill('Belém, Pará');
  await page.getByLabel('Data inicial').fill('2026-09-13');
  let request = page.waitForRequest('**/api/v1/risk?*');
  await page.getByRole('button',{name:'Consultar previsão'}).click();
  let url = new URL((await request).url());
  expect(Object.fromEntries(url.searchParams)).toEqual({location_text:'Belém, Pará',start_date:'2026-09-13',temperature_unit:'celsius'});
  await page.goto(TARGET_URL);
  await page.getByLabel('Buscar por').selectOption('coordinates');
  await expect(page.getByLabel('Cidade',{exact:true})).toBeHidden();
  await expect(page.getByLabel('Latitude',{exact:true})).toBeVisible();
  await page.getByLabel('Latitude',{exact:true}).fill('-1.45');
  await page.getByLabel('Longitude',{exact:true}).fill('-48.49');
  await page.getByLabel('Data inicial').fill('2026-09-13');
  request=page.waitForRequest('**/api/v1/risk?*');
  await page.getByRole('button',{name:'Consultar previsão'}).click();
  url = new URL((await request).url());
  expect(Object.fromEntries(url.searchParams)).toEqual({latitude:'-1.45',longitude:'-48.49',start_date:'2026-09-13',temperature_unit:'celsius'});
  console.log('T21 PASS: página, modo, rótulos e campos contratados nos dois envios.');
 } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exit(1)});
```

## Arquivo: playwright-test-climaprev-t22.js

```javascript
const {chromium, expect} = require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const {fixture} = require('/tmp/climaprev-browser-fixture.cjs');
const TARGET_URL=process.env.CLIMAPREV_UI_URL || 'http://127.0.0.1:18000';
(async () => {
 const browser=await chromium.launch({headless:false,executablePath:'/usr/bin/google-chrome'});
 try {
  const context=await browser.newContext({locale:'pt-BR'}); const page=await context.newPage();
  const requests=[]; let reply={status:200,json:fixture()};
  await page.route('**/api/v1/risk?*',route=>{ requests.push(new URL(route.request().url())); return route.fulfill(reply); });
  await page.addInitScript(()=>{const native=window.fetch;window.fetch=(url,options)=>{window.fetchOptions=options;return native(url,options);};});
  await page.goto(TARGET_URL);
  await page.getByLabel('Cidade',{exact:true}).fill(' Belém, Pará ');
  await page.getByLabel('Data inicial').fill('2026-09-13');
  await page.getByRole('button',{name:'Consultar previsão'}).click();
  await expect(page.getByRole('status')).toContainText('Belém, Pará');
  expect(Object.fromEntries(requests[0].searchParams)).toEqual({location_text:'Belém, Pará',start_date:'2026-09-13',temperature_unit:'celsius'});
  expect(page.url()).toBe(TARGET_URL+'/');
  expect(await page.evaluate(()=>({cache:window.fetchOptions.cache,credentials:window.fetchOptions.credentials,local:localStorage.length,session:sessionStorage.length,cookies:document.cookie}))).toEqual({cache:'no-store',credentials:'omit',local:0,session:0,cookies:''});
  await page.getByLabel('Buscar por').selectOption('coordinates');
  await page.getByLabel('Latitude',{exact:true}).fill('-1.4558');await page.getByLabel('Longitude',{exact:true}).fill('-48.4902');
  await page.getByLabel('Temperatura',{exact:true}).selectOption('fahrenheit');
  await page.getByRole('button',{name:'Consultar previsão'}).click();
  await expect.poll(()=>requests.length).toBe(2);
  expect(Object.fromEntries(requests[1].searchParams)).toEqual({latitude:'-1.4558',longitude:'-48.4902',start_date:'2026-09-13',temperature_unit:'fahrenheit'});
  const call=()=>page.evaluate(async()=>{const {queryRisk}=await import('/assets/api.js');try{return {ok:true,data:await queryRisk(new FormData(document.querySelector('form')))};}catch(e){return {ok:false,code:e.code,status:e.status,requestId:e.requestId,retryAfter:e.retryAfter};}});
  reply={status:422,json:{error:{code:'INVALID_PERIOD',message:'date period is invalid',request_id:'error-422'}}};
  expect(await call()).toEqual({ok:false,code:'INVALID_PERIOD',status:422,requestId:'error-422',retryAfter:60});
  reply={status:200,body:'not json',headers:{'Content-Type':'application/json','X-Request-ID':'malformed-200'}};
  expect(await call()).toEqual({ok:false,code:'MALFORMED_RESPONSE',status:200,requestId:'malformed-200',retryAfter:60});
  reply={status:200,json:{}};
  expect((await call()).code).toBe('MALFORMED_RESPONSE');
  reply={status:200,json:fixture()};
  const success=await call();expect(success.ok).toBe(true);expect(success.data).toEqual(fixture());
  console.log('T22 PASS: 7 cenários, contrato completo, erros, JSON inválido, parâmetros e ausência de persistência.');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
```

## Arquivo: playwright-test-climaprev-t23.js

```javascript
const {chromium, expect}=require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const {fixture}=require('/tmp/climaprev-browser-fixture.cjs');
const TARGET_URL=process.env.CLIMAPREV_UI_URL || 'http://127.0.0.1:18000';
(async()=>{
 const browser=await chromium.launch({headless:false,executablePath:'/usr/bin/google-chrome'});
 try {
  const page=await browser.newPage({locale:'pt-BR',viewport:{width:1280,height:960}}); let payload=fixture(); let requests=0;
  await page.route('**/api/v1/risk?*',route=>{requests++;return route.fulfill({json:payload});});
  await page.goto(TARGET_URL);await page.getByLabel('Cidade',{exact:true}).fill('Belém');await page.getByLabel('Data inicial').fill('2026-09-13');await page.getByLabel('Data final').fill('2026-09-14');
  const submit=async data=>{payload=data;const n=requests;await page.getByRole('button',{name:'Consultar previsão'}).click();await expect.poll(()=>requests).toBe(n+1);await expect(page.getByRole('status')).toContainText('Previsão recebida');};
  const result=page.locator('#result');
  await submit(payload);
  for(const text of ['Belém, Pará','America/Belem','13/09/2026','14/09/2026','Open-Meteo (fixture local)','13/09/2026, 09:00','Dados para avaliação: completos','Moderado','Estimativa baseada em previsão. Não substitui alertas oficiais nem uma avaliação local.','24 °C','32 °C','18 mm','16 km/h']) await expect(result).toContainText(text);
  expect(await result.getByRole('heading',{name:'Estimativa de risco'}).count()).toBe(1);
  await result.getByText('Todas as medições',{exact:true}).first().click();
  for(const text of ['28 °C','82 %','75 %','8 mm/h','28 km/h','Código meteorológico','3']) await expect(result.locator('.day').first()).toContainText(text);
  await page.screenshot({path:'/tmp/climaprev-t23-desktop.png',fullPage:true});
  await page.setViewportSize({width:360,height:860});await page.screenshot({path:'/tmp/climaprev-t23-mobile.png',fullPage:true});await page.setViewportSize({width:1280,height:960});
  const partial=fixture({data_quality:{is_stale:false,missing_fields:['days.2026-09-13.wind_gust_max_kmh'],completeness:'partial'}});partial.days[0].wind_gust_max_kmh=null;
  await submit(partial);await expect(result).toContainText('Dados incompletos');await expect(result).toContainText('Moderado');await expect(result).toContainText('Não disponível');
  await result.getByText('Ver medições ausentes (1)',{exact:true}).click();await expect(result.locator('.missing-fields')).toContainText('Rajada máxima · 13/09/2026');
  const unavailable=fixture({forecast_risk:{level:'low',method:'forecast_heuristic',policy_version:'reference-v1',conditions:[]},data_quality:{is_stale:false,missing_fields:[],completeness:'unavailable'}});
  unavailable.days=unavailable.days.map(d=>Object.fromEntries(Object.entries(d).map(([k,v])=>[k,k==='date'?v:null])));
  await submit(unavailable);await expect(result).toContainText('Dados insuficientes para avaliar o risco');await expect(result).not.toContainText('Baixo');await expect(result).not.toContainText('0 °C');
  await submit(fixture({data_quality:{is_stale:true,missing_fields:[],completeness:'complete'}}));await expect(result).toContainText('Previsão desatualizada');await expect(result).toContainText('13/09/2026, 09:00');
  for(const [status,message] of [['not_configured','Fonte de alertas oficiais ainda não integrada'],['unavailable','Alertas oficiais indisponíveis'],['available','A fonte consultada não retornou alertas para esta consulta']]) {await submit(fixture({official_alerts:{status,items:[]}}));await expect(result).toContainText(message);}
  const malicious='<img src=x onerror="window.maliciousRan=true">';
  const attack=fixture({disclaimer:malicious,official_alerts:{status:'available',items:[{source:malicious,event:malicious,severity:'moderate',effective_at:'2026-09-13T12:00:00Z',expires_at:null,geographic_scope:malicious,source_url:'javascript:window.maliciousRan=true'}]}});
  attack.location.name=malicious;attack.forecast_risk.conditions[0].reason=malicious;
  await submit(attack);await expect(result).toContainText(malicious);expect(await result.locator('img,script').count()).toBe(0);expect(await result.locator('a[href^="javascript:"]').count()).toBe(0);expect(await page.evaluate(()=>window.maliciousRan)).toBeUndefined();
  await expect(result.locator('.alerts h4')).toHaveText(malicious);for(const text of [`Fonte: ${malicious} · Severidade: moderate`,`Área: ${malicious}`,'Início: 13/09/2026, 09:00 · Fim: Não informado','Referência da fonte: javascript:window.maliciousRan=true'])await expect(result.locator('.alerts')).toContainText(text);
  const fahrenheit=fixture({temperature_unit:'fahrenheit'});fahrenheit.days.forEach(d=>{for(const k of ['temperature_min','temperature_max','temperature_mean'])d[k]=d[k]*1.8+32;});
  await submit(fahrenheit);await expect(result).toContainText('75,2 °F');await expect(result).toContainText('89,6 °F');await expect(result).toContainText('18 mm');await expect(result).toContainText('16 km/h');
  const optionalNull=fixture();optionalNull.days[0].humidity_mean_pct=null;optionalNull.data_quality.missing_fields=['days.2026-09-13.humidity_mean_pct'];
  await submit(optionalNull);await expect(result).toContainText('Dados para avaliação: completos');await expect(result).toContainText('Não disponível');
  const partialHigh=fixture({forecast_risk:{level:'high',method:'forecast_heuristic',policy_version:'reference-v1',conditions:[{type:'temperature_extreme_proxy',severity:'high',value:104,unit:'fahrenheit',reason:'Temperatura extrema prevista.'}]},data_quality:{is_stale:false,missing_fields:['days.2026-09-13.wind_gust_max_kmh'],completeness:'partial'}});
  await submit(partialHigh);await expect(result).toContainText('Alto');await expect(result).toContainText('Dados incompletos');await expect(result).toContainText('104 °F');
  const low=fixture({forecast_risk:{level:'low',method:'forecast_heuristic',policy_version:'reference-v1',conditions:[]}});low.days.forEach(day=>{day.precipitation_sum_mm=0;day.wind_max_kmh=0;});await submit(low);await expect(result).toContainText('Baixo');await expect(result).toContainText('0 mm');await expect(result).toContainText('0 km/h');await expect(result.locator('.methodology')).toContainText('forecast_heuristic · Política: reference-v1');
  console.log('T23 PASS: B03–B06, B09 marcação inerte, 12 cenários de apresentação; capturas desktop/mobile.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
```

## Arquivo: playwright-test-climaprev-t24.js

```javascript
const {chromium,expect}=require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const {fixture}=require('/tmp/climaprev-browser-fixture.cjs');
const TARGET_URL=process.env.CLIMAPREV_UI_URL||'http://127.0.0.1:18000';
(async()=>{
 const browser=await chromium.launch({headless:false,executablePath:'/usr/bin/google-chrome'});
 try {
  const page=await browser.newPage({locale:'pt-BR'});let reply={json:fixture()},count=0;
  await page.route('**/api/v1/risk?*',route=>{count++;return reply.hold?undefined:reply.abort?route.abort('failed'):route.fulfill(reply);});
  await page.goto(TARGET_URL);const status=page.getByRole('status'),button=page.getByRole('button',{name:'Consultar previsão'});
  await page.getByLabel('Cidade',{exact:true}).fill('Belém');await page.getByLabel('Data inicial').fill('2026-09-13');
  await button.click();await expect(page.locator('#result')).toBeVisible();
  for(const [http,code,message,focus] of [[404,'LOCATION_NOT_FOUND','Local não encontrado','location_text'],[422,'INVALID_PERIOD','Revise o período','start_date'],[422,'INVALID_TEMPERATURE_UNIT','Revise a unidade','temperature_unit'],[422,'INVALID_LOCATION_INPUT','Revise a cidade','location_text'],[502,'WEATHER_DATA_INVALID','Previsão indisponível',null],[503,'DEPENDENCY_UNAVAILABLE','Previsão indisponível',null],[500,'INTERNAL_ERROR','Não foi possível concluir',null]]){
   reply={status:http,json:{error:{code,message:'ignored',request_id:`error-${http}`}}};await button.click();await expect(status).toContainText(message);await expect(status).toContainText(`error-${http}`);await expect(page.locator('#result')).toBeHidden();await expect(page.getByLabel('Cidade',{exact:true})).toHaveValue('Belém');if(focus)await expect(page.locator('#'+focus)).toBeFocused();
  }
  reply={abort:true};await button.click();await expect(status).toContainText('Verifique sua conexão');await expect(page.locator('#result')).toBeHidden();
  reply={status:200,body:'{broken',headers:{'X-Request-ID':'bad-json'}};await button.click();await expect(status).toContainText('Não foi possível concluir');await expect(status).toContainText('bad-json');
  await page.clock.install({time:new Date('2026-09-13T12:00:00Z')});await page.clock.pauseAt(new Date('2026-09-13T12:00:01Z'));
  for(const [header,body,seconds]of[['3',JSON.stringify({error:{code:'RATE_LIMIT_EXCEEDED',request_id:'limited'}}),3],['invalid','{}',60],[undefined,'{}',60],['5','not json',5]]){
   reply={status:429,body,headers:{'Content-Type':'application/json',...(header?{'Retry-After':header}:{})}};
   await button.click();await expect(status).toContainText(`Aguarde ${seconds} s`);await expect(button).toBeDisabled();const before=count;
   await page.evaluate(()=>document.querySelector('form').requestSubmit());expect(count).toBe(before);
   await page.clock.runFor((seconds-1)*1000);await expect(button).toBeDisabled();expect(count).toBe(before);
   await page.clock.runFor(1000);await expect(button).toBeEnabled();await expect(status).toContainText('Você já pode consultar novamente');expect(count).toBe(before);
  }
  reply={status:429,json:{error:{code:'RATE_LIMIT_EXCEEDED',request_id:'late-timer'}},headers:{'Retry-After':'3'}};await button.click();await expect(button).toBeDisabled();
  await page.clock.setSystemTime((await page.evaluate(()=>Date.now()))+5000);reply={hold:true};
  await page.evaluate(()=>document.querySelector('form').requestSubmit());await expect(status).toContainText('Consultando');await expect(button).toBeEnabled();
  await page.clock.runFor(1000);await expect(status).toContainText('Consultando');await expect(page.locator('form')).toHaveAttribute('aria-busy','true');
  await page.close();
  const race=await browser.newPage({locale:'pt-BR'});
  await race.addInitScript(payload=>{
   const native=window.fetch;window.pending=[];
   window.fetch=(url,options)=>String(url).includes('/api/v1/risk?')?new Promise(resolve=>{window.pending.push({resolve,signal:options.signal});}):native(url,options);
   window.resolveQuery=(index,name)=>{const result=structuredClone(payload);result.location.name=name;window.pending[index].resolve(new Response(JSON.stringify(result),{status:200}));};
  },fixture());
  await race.goto(TARGET_URL);await race.getByLabel('Cidade',{exact:true}).fill('Consulta A');await race.getByLabel('Data inicial').fill('2026-09-13');await race.getByRole('button',{name:'Consultar previsão'}).click();await expect(race.getByRole('status')).toContainText('Consultando');await expect(race.locator('form')).toHaveAttribute('aria-busy','true');
  await race.getByLabel('Cidade',{exact:true}).fill('Consulta B');await race.getByRole('button',{name:'Consultar previsão'}).click();
  expect(await race.evaluate(()=>window.pending[0].signal.aborted)).toBe(true);
  await race.evaluate(()=>window.resolveQuery(1,'Resultado B'));await expect(race.locator('#result')).toContainText('Resultado B');
  await race.evaluate(()=>window.resolveQuery(0,'Resultado A'));await race.evaluate(()=>new Promise(resolve=>setTimeout(resolve,0)));
  await expect(race.locator('#result')).toContainText('Resultado B');await expect(race.locator('#result')).not.toContainText('Resultado A');await expect(race.getByRole('status')).toContainText('Resultado B');await expect(race.locator('form')).toHaveAttribute('aria-busy','false');
  await race.close();
  const nativePage=await browser.newPage();let firstRoute;let failed=false;
  nativePage.on('requestfailed',request=>{if(request.url().includes('location_text=A'))failed=request.failure().errorText.includes('ABORTED');});
  await nativePage.route('**/api/v1/risk?*',route=>{if(new URL(route.request().url()).searchParams.get('location_text')==='A'){firstRoute=route;return;}const data=fixture();data.location.name='Native B';return route.fulfill({json:data});});
  await nativePage.goto(TARGET_URL);await nativePage.getByLabel('Cidade',{exact:true}).fill('A');await nativePage.getByLabel('Data inicial').fill('2026-09-13');await nativePage.getByRole('button',{name:'Consultar previsão'}).click();await expect.poll(()=>!!firstRoute).toBe(true);
  await nativePage.getByLabel('Cidade',{exact:true}).fill('B');await nativePage.getByRole('button',{name:'Consultar previsão'}).click();await expect(nativePage.locator('#result')).toContainText('Native B');await expect.poll(()=>failed).toBe(true);
  await nativePage.close();
  console.log('T24 PASS: erros/foco/contexto, 429 com relógio, sem retry automático, abort+sequência inclusive resposta que ignora abort.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
```

## Arquivo: playwright-test-climaprev-t25.js

```javascript
const {chromium,expect}=require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const {fixture}=require('/tmp/climaprev-browser-fixture.cjs');
const TARGET_URL=process.env.CLIMAPREV_UI_URL||'http://127.0.0.1:18000';
(async()=>{
 const browser=await chromium.launch({headless:false,executablePath:'/usr/bin/google-chrome'});
 try {
  for(const width of [360,1280]) {
   const page=await browser.newPage({viewport:{width,height:960},locale:'pt-BR'});const requests=[];const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/api/v1/risk?*',route=>{requests.push(new URL(route.request().url()));const data=fixture();data.period.end_date='2026-09-13';data.days=data.days.slice(0,1);return route.fulfill({json:data});});
   await page.goto(TARGET_URL);await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:'Ir para a consulta'})).toBeFocused();await expect(page.getByRole('link',{name:'Ir para a consulta'})).toBeVisible();
   expect(await page.getByRole('link',{name:'Ir para a consulta'}).evaluate(el=>getComputedStyle(el).outlineWidth)).toBe('3px');
   await page.screenshot({path:`/tmp/climaprev-keyboard-${width}.png`});
   await page.keyboard.press('Enter');await page.keyboard.press('Tab');await expect(page.getByLabel('Buscar por')).toBeFocused();
   await page.keyboard.press('End');await expect(page.getByLabel('Buscar por')).toHaveValue('coordinates');
   await page.keyboard.press('Tab');await expect(page.getByLabel('Latitude',{exact:true})).toBeFocused();await page.keyboard.type('-1.4558');
   await page.keyboard.press('Tab');await expect(page.getByLabel('Longitude',{exact:true})).toBeFocused();await page.keyboard.type('-48.4902');
   await page.keyboard.press('Tab');await expect(page.getByLabel('Data inicial')).toBeFocused();await page.keyboard.type('09132026');
   await expect(page.getByLabel('Data inicial')).toHaveValue('2026-09-13');
   // Date controls have multiple native keyboard segments. Advance through them.
   for(let i=0;i<12;i++){await page.keyboard.press('Tab');if(await page.getByLabel('Temperatura',{exact:true}).evaluate(el=>el===document.activeElement))break;}
   await expect(page.getByLabel('Temperatura',{exact:true})).toBeFocused();await page.keyboard.press('Tab');await expect(page.getByRole('button',{name:'Consultar previsão'})).toBeFocused();await page.keyboard.press('Enter');
   await expect(page.locator('#result')).toBeVisible();expect(Object.fromEntries(requests[0].searchParams)).toEqual({latitude:'-1.4558',longitude:'-48.4902',start_date:'2026-09-13',temperature_unit:'celsius'});
   await expect(page.getByRole('status')).toHaveAttribute('aria-live','polite');await expect(page.getByRole('status')).toContainText('Previsão recebida');
   for(let i=0;i<5;i++){await page.keyboard.press('Tab');if(await page.locator('.day-details summary').first().evaluate(el=>el===document.activeElement))break;}
   await expect(page.locator('.day-details summary').first()).toBeFocused();await page.keyboard.press('Enter');await expect(page.locator('.day-details').first()).toHaveAttribute('open','');
   expect(await page.evaluate(()=>({viewport:window.innerWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth}))).toEqual({viewport:width,overflow:false});
   const labels=await page.locator('input:not(:disabled),select').evaluateAll(fields=>fields.every(field=>field.labels.length>0));expect(labels).toBe(true);
   await page.evaluate(()=>{document.activeElement.blur();window.scrollTo(0,0);});await page.screenshot({path:`/tmp/climaprev-final-${width}.png`,fullPage:true});
   expect(errors).toEqual([]);await page.close();
  }
  const page=await browser.newPage();let count=0;await page.route('**/api/v1/risk?*',route=>{count++;return route.fulfill({json:fixture()});});await page.goto(TARGET_URL);
  await page.getByLabel('Data inicial').fill('2026-09-13');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);await expect(page.getByLabel('Cidade',{exact:true})).toBeFocused();
  await page.getByLabel('Cidade',{exact:true}).fill('  ');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);
  await page.getByLabel('Cidade',{exact:true}).fill('Belém');await page.getByLabel('Data final').fill('2026-09-20');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);await expect(page.getByLabel('Data final')).toBeFocused();
  await page.getByLabel('Data final').fill('2026-09-12');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);
  await page.getByLabel('Data final').fill('');await page.getByLabel('Buscar por').selectOption('coordinates');await page.getByLabel('Latitude',{exact:true}).fill('-1');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);await expect(page.getByLabel('Longitude',{exact:true})).toBeFocused();
  await page.getByLabel('Longitude',{exact:true}).fill('-48');await page.getByLabel('Latitude',{exact:true}).fill('91');await page.getByRole('button',{name:'Consultar previsão'}).click();expect(count).toBe(0);await expect(page.getByLabel('Latitude',{exact:true})).toBeFocused();
  await page.getByLabel('Latitude',{exact:true}).fill('-1');await page.getByLabel('Data final').fill('2026-09-19');await page.getByRole('button',{name:'Consultar previsão'}).click();await expect.poll(()=>count).toBe(1);await expect(page.locator('#result')).toBeVisible();
  const noScript=await browser.newPage({javaScriptEnabled:false});await noScript.goto(TARGET_URL);await expect(noScript.getByRole('button',{name:'Consultar previsão'})).toBeDisabled();await expect(noScript.locator('noscript')).toBeVisible();await noScript.close();
  console.log('T25 PASS: B02 fronteiras, B10 teclado completo360/1280, labels, foco, live, sem overflow/erros; capturas finais.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
```

## Arquivo: playwright-test-climaprev-tls.js

```javascript
const {chromium,expect}=require('/home/ney/.codex/skills/playwright-skill/node_modules/playwright/test');
const fs=require('fs'),path=require('path'),cp=require('child_process');
const TARGET_URL=process.env.CLIMAPREV_TLS_URL||'https://localhost:18443';
const CA_PATH=process.env.CLIMAPREV_CA_PATH||'/home/ney/Documentos/clima prev/climaprev/.homolog/ca.crt';
(async()=>{
 const dir=fs.mkdtempSync('/tmp/climaprev-browser-homolog-');fs.chmodSync(dir,0o700);const profile=path.join(dir,'profile');let context;
 const launch=()=>chromium.launchPersistentContext(profile,{headless:false,executablePath:'/usr/bin/google-chrome',locale:'pt-BR'});
 try {
  context=await launch();let page=await context.newPage();let rejected=false;
  try{await page.goto(TARGET_URL);}catch(e){rejected=String(e).includes('ERR_CERT_AUTHORITY_INVALID');}
  expect(rejected).toBe(true);await page.close();page=await context.newPage();
  await page.goto('chrome://certificate-manager/localcerts/usercerts');await page.getByRole('button',{name:'Import to Trusted Certificates',exact:true}).waitFor();await context.close();context=null;
  const der=path.join(dir,'ca.der');cp.execFileSync('openssl',['x509','-in',CA_PATH,'-outform','DER','-out',der]);
  cp.execFileSync('python3',['-c',"import sys,sqlite3,hashlib,pathlib; data=pathlib.Path(sys.argv[2]).read_bytes(); c=sqlite3.connect(sys.argv[1]); c.execute('INSERT OR REPLACE INTO certificates VALUES (?,?,?)',(hashlib.sha256(data).hexdigest(),data,bytes.fromhex('0a020803'))); c.commit(); c.close()",path.join(profile,'Default','ServerCertificate'),der]);
  context=await launch();page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(error.message));
  const response=await page.goto(TARGET_URL);expect(response.status()).toBe(200);await expect(page.getByRole('heading',{name:'Sua consulta'})).toBeVisible();await expect(page.getByRole('button',{name:'Consultar previsão'})).toBeEnabled();
  for(const asset of ['styles.css','app.js','api.js','result.js']){const status=await page.evaluate(async name=>(await fetch('/assets/'+name)).status,asset);expect(status).toBe(200);}
  expect(await page.evaluate(async()=>(await fetch('/internal/metrics')).status)).toBe(404);expect(errors).toEqual([]);
  console.log('Browser TLS PASS: CA desconhecida rejeitada; CA local confiável somente no perfil descartável; página/assets200 e internal404 sem bypassTLS.');
 }finally{if(context)await context.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exit(1)});
```

## Arquivo: climaprev-check-runtime-assets.py

```python
import asyncio
import importlib.util
import os
from pathlib import Path

import httpx
import climaprev
from climaprev.main import app

async def main():
    web = Path(climaprev.__file__).parent / 'web'
    assert os.getuid() == 10001
    assert '/opt/venv/' in str(web)
    assert all((web / name).is_file() for name in ('index.html','styles.css','app.js','api.js','result.js'))
    assert importlib.util.find_spec('pytest') is None
    assert not Path('/app/tests').exists()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://runtime') as client:
        response=await client.get('/')
        assert response.status_code==200
        assert 'Clima Prev' in response.text
        for name in ('styles.css','app.js','api.js','result.js'):
            response=await client.get('/assets/'+name)
            assert response.status_code==200
    print('Runtime assets PASS: wheel instalado, UID10001, sempytest/tests, root/assets200.')
asyncio.run(main())
```
