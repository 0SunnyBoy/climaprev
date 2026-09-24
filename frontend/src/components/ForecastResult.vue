<script setup lang="ts">
import DataQualityNotice from '@/components/DataQualityNotice.vue'
import ForecastDayCard from '@/components/ForecastDayCard.vue'
import OfficialAlerts from '@/components/OfficialAlerts.vue'
import RiskSummary from '@/components/RiskSummary.vue'
import type { RiskResponse } from '@/types/api'
import { formatDate, formatDateTime, missingLabel, temperatureUnit } from '@/utils/formatters'

defineProps<{ data: RiskResponse }>()
</script>

<template>
  <section id="result" tabindex="-1" aria-label="Resultado da consulta">
    <header class="result-heading">
      <div>
        <p class="eyebrow">02 · PREVISÃO DO TEMPO</p>
        <h2>{{ data.location.name }}</h2>
        <p class="result-period">{{ formatDate(data.period.start_date) }} a {{ formatDate(data.period.end_date) }} · {{ data.location.timezone }}</p>
      </div>
      <div class="source-note">
        <p>Fonte: {{ data.source.provider }}</p>
        <p>Coleta: {{ formatDateTime(data.source.fetched_at, data.location.timezone) }}</p>
        <p>{{ data.location.latitude }}°, {{ data.location.longitude }}° · Horários no fuso do local</p>
      </div>
    </header>
    <DataQualityNotice :stale="data.data_quality.is_stale" />
    <RiskSummary :risk="data.forecast_risk" :completeness="data.data_quality.completeness" />
    <details v-if="data.data_quality.missing_fields.length" class="missing-fields">
      <summary>Ver medições ausentes ({{ data.data_quality.missing_fields.length }})</summary>
      <ul>
        <li v-for="field in data.data_quality.missing_fields" :key="field">{{ missingLabel(field) }}</li>
      </ul>
    </details>
    <section class="days">
      <h3>Previsão por dia</h3>
      <ForecastDayCard v-for="day in data.days" :key="day.date" :day="day" :unit="temperatureUnit(data.temperature_unit)" />
    </section>
    <OfficialAlerts :alerts="data.official_alerts" :timezone="data.location.timezone" />
    <p class="disclaimer">{{ data.disclaimer }}</p>
    <details class="methodology">
      <summary>Sobre esta estimativa</summary>
      <p>Método: {{ data.forecast_risk.method }} · Política: {{ data.forecast_risk.policy_version }}</p>
      <p>Local identificado por: {{ data.location.source }}</p>
      <p>Referência da consulta: {{ data.request_id }}</p>
    </details>
  </section>
</template>
