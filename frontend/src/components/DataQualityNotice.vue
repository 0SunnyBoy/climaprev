<script setup lang="ts">
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

defineProps<{ stale: boolean }>()
</script>

<template>
  <p v-if="stale" class="notice stale-notice">
    {{ t('staleNotice') }}
  </p>
</template>
