<script setup lang="ts">
import type { OfficialAlerts } from '@/types/api'
import { formatDateTime } from '@/utils/formatters'
import { useLocale } from '@/composables/useLocale'

defineProps<{
  alerts: OfficialAlerts
  timezone: string
}>()

const { locale, t } = useLocale()
</script>

<template>
  <section class="alerts">
    <h3>{{ t('officialAlerts') }}</h3>
    <p v-if="alerts.status === 'not_configured'">{{ t('alertsNotConfigured') }}</p>
    <p v-else-if="alerts.status === 'unavailable'">{{ t('alertsUnavailable') }}</p>
    <p v-else-if="!alerts.items.length">{{ t('noAlerts') }}</p>
    <article v-for="alert in alerts.items" v-else :key="`${alert.source}-${alert.event}-${alert.effective_at}`">
      <h4>{{ alert.event }}</h4>
      <p>{{ t('source') }}: {{ alert.source }} · {{ t('severity') }}: {{ alert.severity }}</p>
      <p>{{ t('area') }}: {{ alert.geographic_scope }}</p>
      <p>{{ t('beginning') }}: {{ formatDateTime(alert.effective_at, timezone, locale) }} · {{ t('ending') }}: {{ alert.expires_at ? formatDateTime(alert.expires_at, timezone, locale) : t('notInformed') }}</p>
      <p v-if="alert.source_url">{{ t('sourceReference') }}: {{ alert.source_url }}</p>
    </article>
  </section>
</template>
