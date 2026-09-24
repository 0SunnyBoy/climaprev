<script setup lang="ts">
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

defineProps<{
  message: string
  role: 'status' | 'alert'
  showResult: boolean
  cooldownSeconds: number
}>()
</script>

<template>
  <div id="query-status" class="query-status" :role="role" aria-atomic="true">
    {{ message }} <a v-if="showResult" href="#result">{{ t('resultLink') }}</a>
  </div>
  <p v-if="cooldownSeconds > 0" class="cooldown-countdown" aria-live="off">{{ t('timeRemaining') }}: {{ cooldownSeconds }} s</p>
</template>
