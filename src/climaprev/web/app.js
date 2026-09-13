import {queryRisk} from './api.js';

const form = document.querySelector('#query-form');
const mode = document.querySelector('#location-mode');
const city = document.querySelector('#city-fields');
const coordinates = document.querySelector('#coordinate-fields');

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
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const start = form.elements.start_date;
  const end = form.elements.end_date;
  const location = form.elements.location_text;
  if (!location.disabled && !location.value.trim()) {
    location.setCustomValidity('Informe uma cidade.');
  }
  if (end.value && (end.value < start.value || (Date.parse(end.value) - Date.parse(start.value)) / 86400000 >= 7)) {
    end.setCustomValidity('Escolha um período de até 7 dias, com a data final após a inicial.');
  }
  if (!form.reportValidity()) return;
  const status = document.querySelector('#query-status');
  status.textContent = 'Consultando a previsão…';
  try {
    const result = await queryRisk(new FormData(form));
    status.textContent = `Previsão recebida para ${result.location.name}.`;
  } catch (error) {
    status.textContent = `Não foi possível concluir a consulta. Tente novamente. ${error.requestId ? `Referência: ${error.requestId}` : ''}`;
  }
});
form.addEventListener('formdata', (event) => {
  if (!event.formData.get('end_date')) event.formData.delete('end_date');
});
