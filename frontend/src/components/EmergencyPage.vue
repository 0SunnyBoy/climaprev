<script setup lang="ts">
import { computed } from 'vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const emergencyNumbers = computed(() => [
  { number: '190', service: t('police'), description: t('policeDescription') },
  { number: '192', service: t('samu'), description: t('samuDescription') },
  { number: '193', service: t('firefighters'), description: t('firefightersDescription') },
  { number: '199', service: t('civilDefense'), description: t('civilDefenseDescription') },
  { number: '191', service: t('federalRoadPolice'), description: t('federalRoadPoliceDescription') },
  { number: '198', service: t('stateRoadPolice'), description: t('stateRoadPoliceDescription') },
])
</script>

<template>
  <section id="emergencia" class="emergency-page" aria-labelledby="emergency-title" tabindex="-1">
    <a class="back-link" href="#consulta">{{ t('emergencyBack') }}</a>
    <div class="emergency-intro">
      <p class="eyebrow">{{ t('emergencyEyebrow') }}</p>
      <h1 id="emergency-title">{{ t('emergencyTitle') }}</h1>
      <p>{{ t('emergencyIntro') }}</p>
      <p class="emergency-national-notice" role="note">{{ t('emergencyNationalNotice') }}</p>
    </div>

    <div class="emergency-grid" :aria-label="t('emergencyServices')">
      <article v-for="item in emergencyNumbers" :key="item.number" class="emergency-card">
        <div class="emergency-card-header">
          <div>
            <p class="emergency-number">{{ item.number }}</p>
            <h2>{{ item.service }}</h2>
          </div>
          <a class="call-button" :href="`tel:${item.number}`" :aria-label="`${t('call')} ${item.service}, ${item.number}`">{{ t('call') }}</a>
        </div>
        <p>{{ item.description }}</p>
      </article>
    </div>

    <aside class="emergency-disclaimer" aria-labelledby="emergency-disclaimer-title">
      <h2 id="emergency-disclaimer-title">{{ t('emergencyDisclaimerTitle') }}</h2>
      <p>{{ t('emergencyDisclaimer') }}</p>
      <p>{{ t('emergencyDisclaimerClimaPrev') }}</p>
    </aside>
  </section>
</template>
