<script setup lang="ts">
import { computed } from 'vue'
import { useLocale } from '@/composables/useLocale'
import type { ForecastDay } from '@/types/api'
import { formatDate, formatValue, formatWeekday } from '@/utils/formatters'

defineProps<{
  day: ForecastDay
  unit: string
  isPeakRisk?: boolean
}>()

const { locale, t } = useLocale()
const measurements = computed(() => [
  ['temperature_min', t('temperatureMin'), 'temperature'],
  ['temperature_max', t('temperatureMax'), 'temperature'],
  ['temperature_mean', t('temperatureMean'), 'temperature'],
  ['humidity_mean_pct', t('humidityMean'), '%'],
  ['precipitation_sum_mm', t('accumulatedRain'), 'mm'],
  ['precipitation_probability_max_pct', t('rainProbability'), '%'],
  ['precipitation_max_hourly_mm', t('hourlyMaxRain'), 'mm/h'],
  ['wind_max_kmh', t('maxWind'), 'km/h'],
  ['wind_gust_max_kmh', t('maxGust'), 'km/h'],
  ['weather_code', t('weatherCode'), ''],
] as const)
</script>

<template>
  <article class="day" :class="{ 'day-peak-risk': isPeakRisk }">
    <p v-if="isPeakRisk" class="day-risk-marker">{{ t('peakRiskDay') }}</p>
    <div class="day-main">
      <div class="day-date">
        <h4>{{ formatDate(day.date, locale) }}</h4>
        <span>{{ formatWeekday(day.date, locale) }}</span>
      </div>
      <dl class="day-overview">
        <div class="measurement"><dt>{{ locale === 'en' ? 'Min. / Max.' : 'Mín. / Máx.' }}</dt><dd>{{ formatValue(day.temperature_min, unit, locale) }} / {{ formatValue(day.temperature_max, unit, locale) }}</dd></div>
        <div class="measurement"><dt>{{ locale === 'en' ? 'Rain' : 'Chuva' }}</dt><dd>{{ formatValue(day.precipitation_sum_mm, 'mm', locale) }}</dd></div>
        <div class="measurement"><dt>{{ locale === 'en' ? 'Wind' : 'Vento' }}</dt><dd>{{ formatValue(day.wind_max_kmh, 'km/h', locale) }}</dd></div>
      </dl>
    </div>
    <details class="day-details">
      <summary>{{ t('allMeasurements') }}</summary>
      <dl class="all-measurements">
        <div v-for="[key, name, measureUnit] in measurements" :key="key" class="measurement">
          <dt>{{ name }}</dt>
          <dd>{{ formatValue(day[key], measureUnit === 'temperature' ? unit : measureUnit, locale) }}</dd>
        </div>
      </dl>
    </details>
  </article>
</template>
