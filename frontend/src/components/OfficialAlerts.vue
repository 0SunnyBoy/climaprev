<script setup lang="ts">
import type { OfficialAlerts } from '@/types/api'
import { formatDateTime } from '@/utils/formatters'

defineProps<{
  alerts: OfficialAlerts
  timezone: string
}>()
</script>

<template>
  <section class="alerts">
    <h3>Alertas oficiais</h3>
    <p v-if="alerts.status === 'not_configured'">Fonte de alertas oficiais ainda não integrada</p>
    <p v-else-if="alerts.status === 'unavailable'">Alertas oficiais indisponíveis</p>
    <p v-else-if="!alerts.items.length">A fonte consultada não retornou alertas para esta consulta. Isso não confirma ausência de alertas em outras fontes.</p>
    <article v-for="alert in alerts.items" v-else :key="`${alert.source}-${alert.event}-${alert.effective_at}`">
      <h4>{{ alert.event }}</h4>
      <p>Fonte: {{ alert.source }} · Severidade: {{ alert.severity }}</p>
      <p>Área: {{ alert.geographic_scope }}</p>
      <p>Início: {{ formatDateTime(alert.effective_at, timezone) }} · Fim: {{ alert.expires_at ? formatDateTime(alert.expires_at, timezone) : 'Não informado' }}</p>
      <p v-if="alert.source_url">Referência da fonte: {{ alert.source_url }}</p>
    </article>
  </section>
</template>
