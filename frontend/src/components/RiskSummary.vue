<script setup lang="ts">
import { useLocale } from '@/composables/useLocale'
import type { ForecastRisk, DataCompleteness, RiskOverview } from '@/types/api'
import { formatDate, formatValue, temperatureUnit } from '@/utils/formatters'

defineProps<{
  risk: ForecastRisk
  overview: RiskOverview
  completeness: DataCompleteness
}>()

const { locale, t } = useLocale()

function riskLabel(level: string): string {
  return level === 'low' ? t('riskLow') : level === 'moderate' ? t('riskModerate') : t('riskHigh')
}

function conditionLabel(type: string): string {
  const labels: Record<string, string> = {
    heavy_rain_proxy: t('conditionHeavyRain'),
    flooding_risk_proxy: t('conditionFlooding'),
    strong_wind_proxy: t('conditionStrongWind'),
    temperature_extreme_proxy: t('conditionExtremeTemperature'),
  }
  return labels[type] || type
}

function conditionUnit(unit: string): string {
  if (unit === 'celsius' || unit === 'fahrenheit') return temperatureUnit(unit)
  return unit === 'mm/day' ? (locale.value === 'en' ? 'mm/day' : 'mm/dia') : unit
}

function conditionReason(conditionType: string, original: string): string {
  if (locale.value !== 'en') return original
  if (conditionType === 'flooding_risk_proxy') return t('reasonFlooding')
  if (conditionType === 'heavy_rain_proxy') return t('reasonHeavyRain')
  if (conditionType === 'strong_wind_proxy') return t('reasonStrongWind')
  if (conditionType === 'temperature_extreme_proxy') return t('reasonExtremeTemperature')
  return original
}

function peakDays(overview: RiskOverview): string {
  return overview.peak_days.map((day) => formatDate(day, locale.value)).join(', ')
}
</script>

<template>
  <section class="risk-section">
    <div class="risk-title">
      <h3>{{ t('riskEstimate') }}</h3>
      <p>{{ t('wholePeriod') }}</p>
    </div>
    <div class="risk-assessment">
      <p v-if="completeness === 'unavailable'" class="quality-warning">{{ t('insufficientData') }}</p>
      <template v-else>
        <p class="risk-level" :class="`risk-${overview.level}`">{{ riskLabel(overview.level) }}</p>
        <p v-if="overview.source === 'official_alert'" class="official-priority">{{ t('officialRiskPriority') }}</p>
        <p :class="completeness === 'partial' ? 'quality-warning' : 'quality-line'">
          {{ completeness === 'partial' ? t('incompleteData') : t('completeData') }}
        </p>
      </template>
      <p class="risk-explanation">{{ t('riskExplanation') }}</p>
    </div>
  </section>
  <aside v-if="overview.peak_days.length" class="peak-risk" role="status">
    <strong>{{ t('peakRiskTitle') }}</strong>
    <span>{{ peakDays(overview) }}</span>
    <p>{{ t('peakRiskBody') }}</p>
  </aside>
  <ul v-if="completeness !== 'unavailable' && risk.conditions.length" class="conditions">
    <li v-for="condition in risk.conditions" :key="`${condition.type}-${condition.value}-${condition.reason}`">
      <strong>{{ conditionLabel(condition.type) }} · {{ formatValue(condition.value, conditionUnit(condition.unit), locale) }}</strong>
      <p>{{ conditionReason(condition.type, condition.reason) }}</p>
    </li>
  </ul>
</template>
