<script setup lang="ts">
defineProps<{
  message: string
  role: 'status' | 'alert'
  showResult: boolean
  cooldownSeconds: number
}>()
</script>

<template>
  <div id="query-status" class="query-status" :role="role" aria-atomic="true">
    {{ message }} <a v-if="showResult" href="#result">Ir para o resultado</a>
  </div>
  <p v-if="cooldownSeconds > 0" class="cooldown-countdown" aria-live="off">Tempo restante: {{ cooldownSeconds }} s</p>
</template>
