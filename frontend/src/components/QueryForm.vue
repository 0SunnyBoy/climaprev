<script setup lang="ts">
import { reactive, ref } from 'vue'
import LocationAutocomplete from '@/components/LocationAutocomplete.vue'
import { emptyQueryForm, type QueryFormState } from '@/types/query'
import type { LocationCandidate } from '@/types/api'

defineProps<{
  loading: boolean
  cooldownSeconds: number
}>()

const emit = defineEmits<{
  submit: [state: QueryFormState]
  cancel: []
  invalid: []
  selected: [candidate: LocationCandidate]
}>()

const formRef = ref<HTMLFormElement | null>(null)
const locationRef = ref<{ focus: () => void } | null>(null)
const form = reactive(emptyQueryForm())

function clearValidity(event: Event) {
  const target = event.target
  if (target instanceof HTMLInputElement || target instanceof HTMLSelectElement) target.setCustomValidity('')
}

function submit() {
  const end = formRef.value?.elements.namedItem('end_date') as HTMLInputElement | null
  if (end) {
    end.setCustomValidity('')
    if (form.endDate && (form.endDate < form.startDate
      || (Date.parse(form.endDate) - Date.parse(form.startDate)) / 86_400_000 >= 7)) {
      end.setCustomValidity('Escolha um período de até 7 dias, com a data final igual ou posterior à inicial.')
    }
  }
  if (!formRef.value?.reportValidity()) {
    emit('invalid')
    return
  }
  emit('submit', { ...form })
}

function focusField(name: string) {
  if (name === 'location_text') locationRef.value?.focus()
  else (formRef.value?.elements.namedItem(name) as HTMLElement | null)?.focus()
}

defineExpose({ focusField })
</script>

<template>
  <form
    id="query-form"
    ref="formRef"
    autocomplete="off"
    action="/api/v1/risk"
    method="post"
    :aria-busy="loading"
    @submit.prevent="submit"
    @input="clearValidity"
  >
    <div class="location-row">
      <div class="field mode-field">
        <label for="location-mode">Buscar por</label>
        <select id="location-mode" v-model="form.locationMode">
          <option value="city">Cidade</option>
          <option value="coordinates">Coordenadas</option>
        </select>
      </div>
      <div id="city-fields" class="field city-field" :hidden="form.locationMode === 'coordinates'">
        <LocationAutocomplete
          ref="locationRef"
          v-model="form.locationText"
          :disabled="form.locationMode === 'coordinates'"
          :required="form.locationMode === 'city'"
          @selected="emit('selected', $event)"
        />
      </div>
      <fieldset id="coordinate-fields" class="coordinates" :hidden="form.locationMode !== 'coordinates'" :disabled="form.locationMode !== 'coordinates'">
        <legend>Coordenadas do local</legend>
        <div class="field">
          <label for="latitude">Latitude</label>
          <input id="latitude" v-model="form.latitude" name="latitude" type="number" min="-90" max="90" step="any" placeholder="-1.4558" required />
        </div>
        <div class="field">
          <label for="longitude">Longitude</label>
          <input id="longitude" v-model="form.longitude" name="longitude" type="number" min="-180" max="180" step="any" placeholder="-48.4902" required />
        </div>
      </fieldset>
    </div>
    <div class="period-row">
      <div class="field">
        <label for="start_date">Data inicial</label>
        <input id="start_date" v-model="form.startDate" name="start_date" type="date" required />
      </div>
      <div class="field">
        <label for="end_date">Data final <span class="optional">opcional</span></label>
        <input id="end_date" v-model="form.endDate" name="end_date" type="date" aria-describedby="end-hint" />
        <span id="end-hint" class="field-hint">Em branco: apenas a data inicial.</span>
      </div>
      <div class="field">
        <label for="temperature_unit">Temperatura</label>
        <select id="temperature_unit" v-model="form.temperatureUnit" name="temperature_unit">
          <option value="celsius">Celsius (°C)</option>
          <option value="fahrenheit">Fahrenheit (°F)</option>
        </select>
      </div>
      <button class="primary" type="submit" :disabled="cooldownSeconds > 0">
        Consultar previsão <span aria-hidden="true">↗</span>
      </button>
      <button v-if="loading" id="cancel-query" class="secondary" type="button" @click="emit('cancel')">Cancelar</button>
    </div>
  </form>
</template>
