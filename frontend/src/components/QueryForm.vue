<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import LocationAutocomplete from '@/components/LocationAutocomplete.vue'
import { useLocale } from '@/composables/useLocale'
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

const { t } = useLocale()

const formRef = ref<HTMLFormElement | null>(null)
const locationRef = ref<{ focus: () => void } | null>(null)
const form = reactive(emptyQueryForm())
const fieldErrors = reactive<Record<string, string>>({})

function clearValidity(event: Event) {
  const target = event.target
  if (target instanceof HTMLInputElement || target instanceof HTMLSelectElement) {
    target.setCustomValidity('')
    delete fieldErrors[target.name]
  }
}

function onInvalidField(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return
  fieldErrors[target.name] = target.validationMessage
  emit('invalid')
}

function submit() {
  Object.keys(fieldErrors).forEach((name) => delete fieldErrors[name])
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

function setFieldError(name: string, message: string) {
  fieldErrors[name] = message
  nextTick(() => focusField(name))
}

defineExpose({ setFieldError })
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
    @change="clearValidity"
    @invalid.capture="onInvalidField"
  >
    <div class="location-row">
      <div class="field mode-field">
        <label for="location-mode">{{ t('searchBy') }}</label>
        <select id="location-mode" v-model="form.locationMode">
          <option value="city">{{ t('city') }}</option>
          <option value="coordinates">{{ t('coordinates') }}</option>
        </select>
      </div>
      <div id="city-fields" class="field city-field" :hidden="form.locationMode === 'coordinates'">
        <LocationAutocomplete
          ref="locationRef"
          v-model="form.locationText"
          :disabled="form.locationMode === 'coordinates'"
          :required="form.locationMode === 'city'"
          :error="fieldErrors.location_text"
          @selected="emit('selected', $event)"
        />
      </div>
      <fieldset id="coordinate-fields" class="coordinates" :hidden="form.locationMode !== 'coordinates'" :disabled="form.locationMode !== 'coordinates'">
        <legend>{{ t('coordinatesLegend') }}</legend>
        <div class="field">
          <label for="latitude">{{ t('latitude') }}</label>
          <input id="latitude" v-model="form.latitude" name="latitude" type="number" min="-90" max="90" step="any" placeholder="-1.4558" :aria-invalid="Boolean(fieldErrors.latitude)" :aria-describedby="fieldErrors.latitude ? 'latitude-error' : undefined" required />
          <span v-if="fieldErrors.latitude" id="latitude-error" class="field-error">{{ fieldErrors.latitude }}</span>
        </div>
        <div class="field">
          <label for="longitude">{{ t('longitude') }}</label>
          <input id="longitude" v-model="form.longitude" name="longitude" type="number" min="-180" max="180" step="any" placeholder="-48.4902" :aria-invalid="Boolean(fieldErrors.longitude)" :aria-describedby="fieldErrors.longitude ? 'longitude-error' : undefined" required />
          <span v-if="fieldErrors.longitude" id="longitude-error" class="field-error">{{ fieldErrors.longitude }}</span>
        </div>
      </fieldset>
    </div>
    <div class="period-row">
      <div class="field">
        <label for="start_date">{{ t('startDate') }}</label>
        <input id="start_date" v-model="form.startDate" name="start_date" type="date" :aria-invalid="Boolean(fieldErrors.start_date)" :aria-describedby="fieldErrors.start_date ? 'start-date-error' : undefined" required />
        <span v-if="fieldErrors.start_date" id="start-date-error" class="field-error">{{ fieldErrors.start_date }}</span>
      </div>
      <div class="field">
        <label for="end_date">{{ t('endDate') }} <span class="optional">{{ t('optional') }}</span></label>
        <input id="end_date" v-model="form.endDate" name="end_date" type="date" :aria-invalid="Boolean(fieldErrors.end_date)" :aria-describedby="fieldErrors.end_date ? 'end-hint end-date-error' : 'end-hint'" />
        <span id="end-hint" class="field-hint">{{ t('endDateHint') }}</span>
        <span v-if="fieldErrors.end_date" id="end-date-error" class="field-error">{{ fieldErrors.end_date }}</span>
      </div>
      <div class="field">
        <label for="temperature_unit">{{ t('temperature') }}</label>
        <select id="temperature_unit" v-model="form.temperatureUnit" name="temperature_unit" :aria-invalid="Boolean(fieldErrors.temperature_unit)" :aria-describedby="fieldErrors.temperature_unit ? 'temperature-unit-error' : undefined">
          <option value="celsius">{{ t('celsius') }}</option>
          <option value="fahrenheit">{{ t('fahrenheit') }}</option>
        </select>
        <span v-if="fieldErrors.temperature_unit" id="temperature-unit-error" class="field-error">{{ fieldErrors.temperature_unit }}</span>
      </div>
      <div class="form-actions">
        <button class="primary" type="submit" :disabled="cooldownSeconds > 0">
          {{ t('submitQuery') }} <span aria-hidden="true">↗</span>
        </button>
        <button v-if="loading" id="cancel-query" class="secondary" type="button" @click="emit('cancel')">{{ t('cancel') }}</button>
      </div>
    </div>
  </form>
</template>
