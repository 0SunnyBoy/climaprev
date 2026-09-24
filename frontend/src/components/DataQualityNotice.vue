<script setup lang="ts">
defineProps<{ stale: boolean }>()
</script>

<template>
  <p v-if="stale" class="notice stale-notice">
    Previsão desatualizada. A atualização falhou; estes são dados coletados anteriormente. Você pode consultar novamente.
  </p>
</template>
