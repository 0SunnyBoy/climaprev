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
form.addEventListener('submit', (event) => {
  const start = form.elements.start_date;
  const end = form.elements.end_date;
  const location = form.elements.location_text;
  if (!location.disabled && !location.value.trim()) {
    location.setCustomValidity('Informe uma cidade.');
  }
  if (end.value && (end.value < start.value || (Date.parse(end.value) - Date.parse(start.value)) / 86400000 >= 7)) {
    end.setCustomValidity('Escolha um período de até 7 dias, com a data final após a inicial.');
  }
  if (!form.reportValidity()) event.preventDefault();
});
form.addEventListener('formdata', (event) => {
  if (!event.formData.get('end_date')) event.formData.delete('end_date');
});
