<script setup lang="ts">
import DataQualityNotice from '@/components/DataQualityNotice.vue'
import ForecastDayCard from '@/components/ForecastDayCard.vue'
import OfficialAlerts from '@/components/OfficialAlerts.vue'
import RiskSummary from '@/components/RiskSummary.vue'
import type { RiskResponse } from '@/types/api'
import { formatDate, formatDateTime, missingLabel, temperatureUnit } from '@/utils/formatters'
import { useLocale } from '@/composables/useLocale'

defineProps<{ data: RiskResponse }>()

const { locale, t } = useLocale()
</script>

<template>
  <section id="result" tabindex="-1" :aria-label="t('resultAria')">
    <header class="result-heading">
      <div>
        <p class="eyebrow">{{ t('forecastEyebrow') }}</p>
        <h2>{{ data.location.name }}</h2>
        <p class="result-period">{{ formatDate(data.period.start_date, locale) }} – {{ formatDate(data.period.end_date, locale) }} · {{ data.location.timezone }}</p>
      </div>
      <div class="source-note">
        <p>{{ t('source') }}: {{ data.source.provider }}</p>
        <p>{{ t('collected') }}: {{ formatDateTime(data.source.fetched_at, data.location.timezone, locale) }}</p>
        <p>{{ data.location.latitude }}°, {{ data.location.longitude }}° · {{ t('localTime') }}</p>
      </div>
    </header>
    <DataQualityNotice :stale="data.data_quality.is_stale" />
    <RiskSummary :risk="data.forecast_risk" :completeness="data.data_quality.completeness" />
    <details v-if="data.data_quality.missing_fields.length" class="missing-fields">
      <summary>{{ t('missingMeasurements') }} ({{ data.data_quality.missing_fields.length }})</summary>
      <ul>
        <li v-for="field in data.data_quality.missing_fields" :key="field">{{ missingLabel(field, locale) }}</li>
      </ul>
    </details>
    <section class="days">
      <h3>{{ t('forecastByDay') }}</h3>
      <ForecastDayCard v-for="day in data.days" :key="day.date" :day="day" :unit="temperatureUnit(data.temperature_unit)" />
    </section>
    <OfficialAlerts :alerts="data.official_alerts" :timezone="data.location.timezone" />
    <p class="disclaimer">{{ locale === 'en' ? t('forecastDisclaimer') : data.disclaimer }}</p>
    <details class="methodology">
      <summary>{{ t('aboutEstimate') }}</summary>
      <p>{{ t('method') }}: {{ data.forecast_risk.method }} · {{ t('policy') }}: {{ data.forecast_risk.policy_version }}</p>
      <p>{{ t('identifiedBy') }}: {{ data.location.source }}</p>
      <p>{{ t('requestReference') }}: {{ data.request_id }}</p>
    </details>
  </section>
</template>
