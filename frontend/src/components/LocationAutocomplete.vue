<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useLocationSearch } from '@/composables/useLocationSearch'
import type { LocationCandidate } from '@/types/api'

const props = defineProps<{
  modelValue: string
  disabled?: boolean
  required?: boolean
  error?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  selected: [candidate: LocationCandidate]
}>()

const input = ref<HTMLInputElement | null>(null)
const activeIndex = ref(-1)
const { suggestions, searching, schedule, clear } = useLocationSearch()

const activeDescendant = computed(() => activeIndex.value >= 0
  ? `location-option-${activeIndex.value}`
  : undefined)

watch(() => props.modelValue, (value) => {
  if (input.value && input.value.value !== value) input.value.value = value
})

function update(event: Event) {
  const value = (event.target as HTMLInputElement).value
  activeIndex.value = -1
  emit('update:modelValue', value)
  schedule(value)
}

function select(candidate: LocationCandidate) {
  emit('update:modelValue', candidate.name)
  emit('selected', candidate)
  clear()
  input.value?.focus()
}

function onKeydown(event: KeyboardEvent) {
  if (!suggestions.value.length) return
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, suggestions.value.length - 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, -1)
  } else if (event.key === 'Enter' && activeIndex.value >= 0) {
    event.preventDefault()
    select(suggestions.value[activeIndex.value])
  } else if (event.key === 'Escape') {
    event.preventDefault()
    activeIndex.value = -1
    clear()
  }
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
    role="combobox"
    maxlength="200"
    placeholder="Ex.: Belém, Pará"
    :aria-describedby="error ? 'city-hint city-error' : 'city-hint'"
    :aria-invalid="Boolean(error)"
    :aria-expanded="suggestions.length > 0"
    :aria-controls="suggestions.length ? 'location-suggestions' : undefined"
    :aria-activedescendant="activeDescendant"
    aria-autocomplete="list"
    aria-haspopup="listbox"
    :aria-busy="searching"
    autocomplete="off"
    :value="modelValue"
    :disabled="disabled"
    :required="required"
    @input="update"
    @keydown="onKeydown"
  />
  <span id="city-hint" class="field-hint">Inclua o estado ou país para uma busca mais precisa.</span>
  <span v-if="error" id="city-error" class="field-error">{{ error }}</span>
  <span class="sr-only" role="status">{{ suggestions.length ? `${suggestions.length} sugestões disponíveis após o campo de cidade.` : '' }}</span>
  <ul
    v-if="suggestions.length"
    id="location-suggestions"
    class="location-suggestions"
    aria-label="Sugestões de localidade"
    role="listbox"
  >
    <li
      v-for="(candidate, index) in suggestions"
      :id="`location-option-${index}`"
      :key="`${candidate.name}-${candidate.latitude}-${candidate.longitude}`"
      class="location-suggestion"
      role="option"
      :aria-selected="index === activeIndex"
      @mousedown.prevent
      @click="select(candidate)"
    >
      <span>
        {{ candidate.name }} · {{ candidate.latitude.toFixed(4) }}, {{ candidate.longitude.toFixed(4) }}
      </span>
    </li>
  </ul>
</template>
