<script setup lang="ts">
defineProps<{
  message: string
  role: 'status' | 'alert'
}>()
</script>

<template>
  <div id="query-status" class="query-status" :role="role" aria-live="polite" aria-atomic="true">{{ message }}</div>
</template>
