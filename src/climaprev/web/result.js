const levels = {low:'Baixo', moderate:'Moderado', high:'Alto'};
const units = {celsius:'°C', fahrenheit:'°F', 'mm/day':'mm/dia'};
const conditionNames = {heavy_rain_proxy:'Chuva intensa', flooding_risk_proxy:'Sinal de risco de alagamento', strong_wind_proxy:'Vento forte', temperature_extreme_proxy:'Temperatura extrema'};
const measurements = [
  ['temperature_min','Temperatura mínima','temperature'], ['temperature_max','Temperatura máxima','temperature'],
  ['temperature_mean','Temperatura média','temperature'], ['humidity_mean_pct','Umidade média','%'],
  ['precipitation_sum_mm','Chuva acumulada','mm'], ['precipitation_probability_max_pct','Probabilidade de chuva','%'],
  ['precipitation_max_hourly_mm','Chuva máxima por hora','mm/h'], ['wind_max_kmh','Vento máximo','km/h'],
  ['wind_gust_max_kmh','Rajada máxima','km/h'], ['weather_code','Código meteorológico',''],
];
const numberFormat = new Intl.NumberFormat('pt-BR', {maximumFractionDigits:1});
const date = value => new Intl.DateTimeFormat('pt-BR', {timeZone:'UTC'}).format(new Date(`${value}T12:00:00Z`));
const time = (value, zone) => new Intl.DateTimeFormat('pt-BR', {dateStyle:'short',timeStyle:'short',timeZone:zone}).format(new Date(value));
const value = (number, unit) => number === null ? 'Não disponível' : `${numberFormat.format(number)}${unit ? ` ${unit}` : ''}`;
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function metric(label, content) {
  const pair = element('div', undefined, 'measurement');
  pair.append(element('dt', label), element('dd', content));
  return pair;
}
function missingLabel(field) {
  const day = field.match(/\d{4}-\d{2}-\d{2}/)?.[0];
  const measure = measurements.find(([key]) => field.endsWith(key) || field.endsWith(key.replace(/temperature_(min|max|mean)/, 'temperature_$1_c')));
  const label = field.includes('precipitation.coverage') ? 'Cobertura horária de chuva' : measure?.[1] || field;
  return `${label}${day ? ` · ${date(day)}` : ''}`;
}

export function renderResult(container, data) {
  const content = document.createDocumentFragment();
  const unit = units[data.temperature_unit];
  const header = element('header', undefined, 'result-heading');
  const heading = element('div');
  heading.append(element('p','02 · PREVISÃO DO TEMPO','eyebrow'),element('h2',data.location.name));
  heading.append(element('p', `${date(data.period.start_date)} a ${date(data.period.end_date)} · ${data.location.timezone}`, 'result-period'));
  const coordinateFormat = new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 15});
  const coordinates = `${coordinateFormat.format(data.location.latitude)}°, ${coordinateFormat.format(data.location.longitude)}°`;
  const source = element('div',undefined,'source-note');
  source.append(element('p',`Fonte: ${data.source.provider}`),element('p',`Coleta: ${time(data.source.fetched_at,data.location.timezone)}`),element('p',`${coordinates} · Horários no fuso do local`));
  header.append(heading,source); content.append(header);

  if (data.data_quality.is_stale) content.append(element('p','Previsão desatualizada. A atualização falhou; estes são dados coletados anteriormente. Você pode consultar novamente.', 'notice stale-notice'));
  const risk = element('section',undefined,'risk-section');
  const riskTitle = element('div',undefined,'risk-title'); riskTitle.append(element('h3','Estimativa de risco'),element('p','Para todo o período consultado'));
  const assessment = element('div',undefined,'risk-assessment');
  const completeness = data.data_quality.completeness;
  if (completeness === 'unavailable') {
    assessment.append(element('p','Dados insuficientes para avaliar o risco','quality-warning'));
  } else {
    assessment.append(element('p',levels[data.forecast_risk.level],`risk-level risk-${data.forecast_risk.level}`));
    assessment.append(element('p',completeness === 'partial' ? 'Dados incompletos. Risco calculado com os valores disponíveis.' : 'Dados para avaliação: completos', completeness === 'partial' ? 'quality-warning' : 'quality-line'));
  }
  assessment.append(element('p','Estimativa por regras de previsão; não é um alerta oficial.','risk-explanation'));
  risk.append(riskTitle,assessment);content.append(risk);
  if (completeness !== 'unavailable' && data.forecast_risk.conditions.length) {
    const list=element('ul',undefined,'conditions');
    for (const condition of data.forecast_risk.conditions) {
      const item=element('li');item.append(element('strong',`${conditionNames[condition.type] || condition.type} · ${value(condition.value,units[condition.unit] || condition.unit)}`),element('p',condition.reason));list.append(item);
    }
    content.append(list);
  }
  if (data.data_quality.missing_fields.length) {
    const missing=element('details',undefined,'missing-fields');missing.append(element('summary',`Ver medições ausentes (${data.data_quality.missing_fields.length})`));
    const list=element('ul');for(const field of data.data_quality.missing_fields)list.append(element('li',missingLabel(field)));missing.append(list);content.append(missing);
  }
  const days=element('section',undefined,'days');days.append(element('h3','Previsão por dia'));
  for (const day of data.days) {
    const article=element('article',undefined,'day');
    const main=element('div',undefined,'day-main');
    const label=element('div',undefined,'day-date');label.append(element('h4',date(day.date)),element('span',new Intl.DateTimeFormat('pt-BR',{weekday:'long',timeZone:'UTC'}).format(new Date(`${day.date}T12:00:00Z`))));
    const overview=element('dl',undefined,'day-overview');overview.append(metric('Mín. / Máx.',`${value(day.temperature_min,unit)} / ${value(day.temperature_max,unit)}`),metric('Chuva',value(day.precipitation_sum_mm,'mm')),metric('Vento',value(day.wind_max_kmh,'km/h')));main.append(label,overview);
    const details=element('details',undefined,'day-details');details.append(element('summary','Todas as medições'));
    const measures=element('dl',undefined,'all-measurements');for(const [key,name,measureUnit]of measurements)measures.append(metric(name,value(day[key],measureUnit === 'temperature' ? unit : measureUnit)));
    details.append(measures);article.append(main,details);days.append(article);
  }
  content.append(days);
  const alerts=element('section',undefined,'alerts');alerts.append(element('h3','Alertas oficiais'));
  const status=data.official_alerts.status;
  if(status === 'not_configured') alerts.append(element('p','Fonte de alertas oficiais ainda não integrada'));
  else if(status === 'unavailable') alerts.append(element('p','Alertas oficiais indisponíveis'));
  else if(!data.official_alerts.items.length) alerts.append(element('p','A fonte consultada não retornou alertas para esta consulta. Isso não confirma ausência de alertas em outras fontes.'));
  else for(const alert of data.official_alerts.items) {
    const item=element('article');item.append(element('h4',alert.event),element('p',`Fonte: ${alert.source} · Severidade: ${alert.severity}`),element('p',`Área: ${alert.geographic_scope}`),element('p',`Início: ${time(alert.effective_at,data.location.timezone)} · Fim: ${alert.expires_at ? time(alert.expires_at,data.location.timezone) : 'Não informado'}`));
    if(alert.source_url) item.append(element('p',`Referência da fonte: ${alert.source_url}`));alerts.append(item);
  }
  content.append(alerts,element('p',data.disclaimer,'disclaimer'));
  const methodology=element('details',undefined,'methodology');methodology.append(element('summary','Sobre esta estimativa'),element('p',`Método: ${data.forecast_risk.method} · Política: ${data.forecast_risk.policy_version}`),element('p',`Local identificado por: ${data.location.source}`),element('p',`Referência da consulta: ${data.request_id}`));content.append(methodology);
  container.replaceChildren(content);container.hidden=false;
}
