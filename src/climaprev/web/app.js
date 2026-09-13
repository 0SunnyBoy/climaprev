import {queryRisk} from './api.js';
import {renderResult} from './result.js';

const form = document.querySelector('#query-form');
const mode = document.querySelector('#location-mode');
const city = document.querySelector('#city-fields');
const coordinates = document.querySelector('#coordinate-fields');
const status = document.querySelector('#query-status');
const result = document.querySelector('#result');
const submit = form.querySelector('button[type="submit"]');
let sequence = 0;
let controller;
let retryUntil = 0;
let retryTimer;
submit.disabled = false;

mode.addEventListener('change', () => {
  const useCoordinates = mode.value === 'coordinates';
  city.hidden = useCoordinates;
  city.querySelector('input').disabled = useCoordinates;
  coordinates.hidden = !useCoordinates;
  coordinates.disabled = !useCoordinates;
});

form.addEventListener('input', () => {
  for (const field of form.querySelectorAll('input')) field.setCustomValidity('');
});

function showCooldown(requestId) {
  clearInterval(retryTimer);
  const update = () => {
    const seconds = Math.max(0, Math.ceil((retryUntil - Date.now()) / 1000));
    submit.disabled = seconds > 0;
    status.textContent = seconds > 0
      ? `Limite de consultas atingido. Aguarde ${seconds} s para consultar novamente.${requestId ? ` Referência: ${requestId}` : ''}`
      : 'Você já pode consultar novamente. Use o botão Consultar previsão.';
    if (seconds === 0) clearInterval(retryTimer);
  };
  update();
  if (retryUntil > Date.now()) retryTimer = setInterval(update, 1000);
}

function showError(error) {
  if (error.status === 429) {
    retryUntil = Date.now() + error.retryAfter * 1000;
    showCooldown(error.requestId);
    return;
  }
  let message = 'Não foi possível concluir a consulta. Tente novamente.';
  let field;
  if (error.code === 'NETWORK_ERROR') message = 'Verifique sua conexão e tente novamente.';
  else if (error.code !== 'MALFORMED_RESPONSE') {
    if (error.status === 404) {
      message = 'Local não encontrado. Inclua o estado ou país, ou confira as coordenadas.';
      field = mode.value === 'city' ? form.elements.location_text : form.elements.latitude;
    } else if (error.status === 422) {
      if (error.code === 'INVALID_PERIOD') {
        message = 'Revise o período: use de 1 a 7 dias, com a data final igual ou posterior à inicial.';
        field = form.elements.end_date.value ? form.elements.end_date : form.elements.start_date;
      } else if (error.code === 'INVALID_TEMPERATURE_UNIT') {
        message = 'Revise a unidade de temperatura e consulte novamente.';
        field = form.elements.temperature_unit;
      } else {
        message = 'Revise a cidade ou o par de coordenadas e consulte novamente.';
        field = mode.value === 'city' ? form.elements.location_text : form.elements.latitude;
      }
    } else if (error.status === 502 || error.status === 503) {
      message = 'Previsão indisponível no momento. Tente novamente em instantes.';
    }
  }
  status.textContent = `${message}${error.requestId ? ` Referência: ${error.requestId}` : ''}`;
  field?.focus();
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (Date.now() < retryUntil) return;
  clearInterval(retryTimer);
  submit.disabled = false;
  const requestSequence = ++sequence;
  controller?.abort();
  result.hidden = true;
  result.replaceChildren();
  const start = form.elements.start_date;
  const end = form.elements.end_date;
  const location = form.elements.location_text;
  if (!location.disabled && !location.value.trim()) location.setCustomValidity('Informe uma cidade.');
  if (end.value && (end.value < start.value || (Date.parse(end.value) - Date.parse(start.value)) / 86400000 >= 7)) {
    end.setCustomValidity('Escolha um período de até 7 dias, com a data final igual ou posterior à inicial.');
  }
  if (!form.reportValidity()) {
    form.setAttribute('aria-busy', 'false');
    status.textContent = 'Revise os campos indicados para consultar.';
    return;
  }
  controller = new AbortController();
  form.setAttribute('aria-busy', 'true');
  status.textContent = 'Consultando a previsão… Você pode enviar outra consulta enquanto aguarda.';
  try {
    const data = await queryRisk(new FormData(form), {signal: controller.signal});
    if (requestSequence !== sequence) return;
    renderResult(result, data);
    status.textContent = `Previsão recebida para ${data.location.name}. Confira a qualidade dos dados abaixo.`;
  } catch (error) {
    if (requestSequence !== sequence || error.name === 'AbortError') return;
    result.hidden = true;
    result.replaceChildren();
    showError(error);
  } finally {
    if (requestSequence === sequence) form.setAttribute('aria-busy', 'false');
  }
});
