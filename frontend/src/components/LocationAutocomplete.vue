<script setup lang="ts">
import { ref, watch } from 'vue'
import { useLocationSearch } from '@/composables/useLocationSearch'
import type { LocationCandidate } from '@/types/api'

const props = defineProps<{
  modelValue: string
  disabled?: boolean
  required?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  selected: [candidate: LocationCandidate]
}>()

const input = ref<HTMLInputElement | null>(null)
const { suggestions, schedule, clear } = useLocationSearch()

watch(() => props.modelValue, (value) => {
  if (input.value && input.value.value !== value) input.value.value = value
})

function update(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit('update:modelValue', value)
  schedule(value)
}

function select(candidate: LocationCandidate) {
  emit('update:modelValue', candidate.name)
  emit('selected', candidate)
  clear()
  input.value?.focus()
}

function focus() {
  input.value?.focus()
}

defineExpose({ focus })
</script>

<template>
  <label for="location_text">Cidade</label>
  <input
    id="location_text"
    ref="input"
    name="location_text"
    type="text"
    maxlength="200"
    placeholder="Ex.: Belém, Pará"
    aria-describedby="city-hint"
    autocomplete="off"
    :value="modelValue"
    :disabled="disabled"
    :required="required"
    @input="update"
  />
  <span id="city-hint" class="field-hint">Inclua o estado ou país para uma busca mais precisa.</span>
  <div
    id="location-suggestions"
    class="location-suggestions"
    role="listbox"
    aria-label="Sugestões de localidade"
    :hidden="suggestions.length === 0"
  >
    <button
      v-for="candidate in suggestions"
      :key="`${candidate.name}-${candidate.latitude}-${candidate.longitude}`"
      type="button"
      class="location-suggestion"
      role="option"
      @click="select(candidate)"
    >
      {{ candidate.name }} · {{ candidate.latitude.toFixed(4) }}, {{ candidate.longitude.toFixed(4) }}
    </button>
  </div>
</template>
