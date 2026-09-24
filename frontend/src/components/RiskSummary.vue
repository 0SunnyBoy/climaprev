<script setup lang="ts">
import type { ForecastRisk, DataCompleteness } from '@/types/api'
import { conditionNames, formatValue, riskLevels, units } from '@/utils/formatters'

defineProps<{
  risk: ForecastRisk
  completeness: DataCompleteness
}>()
</script>

<template>
  <section class="risk-section">
    <div class="risk-title">
      <h3>Estimativa de risco</h3>
      <p>Para todo o período consultado</p>
    </div>
    <div class="risk-assessment">
      <p v-if="completeness === 'unavailable'" class="quality-warning">Dados insuficientes para avaliar o risco</p>
      <template v-else>
        <p class="risk-level" :class="`risk-${risk.level}`">{{ riskLevels[risk.level] }}</p>
        <p :class="completeness === 'partial' ? 'quality-warning' : 'quality-line'">
          {{ completeness === 'partial' ? 'Dados incompletos. Risco calculado com os valores disponíveis.' : 'Dados para avaliação: completos' }}
        </p>
      </template>
      <p class="risk-explanation">Estimativa por regras de previsão; não é um alerta oficial.</p>
    </div>
  </section>
  <ul v-if="completeness !== 'unavailable' && risk.conditions.length" class="conditions">
    <li v-for="condition in risk.conditions" :key="`${condition.type}-${condition.value}-${condition.reason}`">
      <strong>{{ conditionNames[condition.type] || condition.type }} · {{ formatValue(condition.value, units[condition.unit] || condition.unit) }}</strong>
      <p>{{ condition.reason }}</p>
    </li>
  </ul>
</template>
