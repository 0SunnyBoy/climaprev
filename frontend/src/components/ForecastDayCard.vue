<script setup lang="ts">
import type { ForecastDay } from '@/types/api'
import { formatDate, formatValue, formatWeekday, measurements } from '@/utils/formatters'

defineProps<{
  day: ForecastDay
  unit: string
}>()
</script>

<template>
  <article class="day">
    <div class="day-main">
      <div class="day-date">
        <h4>{{ formatDate(day.date) }}</h4>
        <span>{{ formatWeekday(day.date) }}</span>
      </div>
      <dl class="day-overview">
        <div class="measurement"><dt>Mín. / Máx.</dt><dd>{{ formatValue(day.temperature_min, unit) }} / {{ formatValue(day.temperature_max, unit) }}</dd></div>
        <div class="measurement"><dt>Chuva</dt><dd>{{ formatValue(day.precipitation_sum_mm, 'mm') }}</dd></div>
        <div class="measurement"><dt>Vento</dt><dd>{{ formatValue(day.wind_max_kmh, 'km/h') }}</dd></div>
      </dl>
    </div>
    <details class="day-details">
      <summary>Todas as medições</summary>
      <dl class="all-measurements">
        <div v-for="[key, name, measureUnit] in measurements" :key="key" class="measurement">
          <dt>{{ name }}</dt>
          <dd>{{ formatValue(day[key], measureUnit === 'temperature' ? unit : measureUnit) }}</dd>
        </div>
      </dl>
    </details>
  </article>
</template>
