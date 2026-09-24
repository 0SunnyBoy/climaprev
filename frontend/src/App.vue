<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import ForecastResult from '@/components/ForecastResult.vue'
import QueryForm from '@/components/QueryForm.vue'
import QueryStatus from '@/components/QueryStatus.vue'
import { QueryError, QueryTimeoutError } from '@/services/api'
import { useRiskQuery } from '@/composables/useRiskQuery'
import { useTheme } from '@/composables/useTheme'
import type { LocationCandidate } from '@/types/api'
import type { QueryFormState } from '@/types/query'

const formRef = ref<{ setFieldError: (name: string, message: string) => void } | null>(null)
const statusMessage = ref('')
const statusRole = ref<'status' | 'alert'>('status')
const retryUntil = ref(0)
const cooldownSeconds = ref(0)
let retryTimer: ReturnType<typeof setInterval> | undefined

const { result, loading, timedOut, error, submit, cancel } = useRiskQuery()
const { isDark, toggleTheme } = useTheme()
const hasResult = computed(() => result.value !== null)

function clearCooldown() {
  if (retryTimer) clearInterval(retryTimer)
  retryTimer = undefined
  cooldownSeconds.value = 0
}

function updateCooldown(requestId: string, seconds: number) {
  clearCooldown()
  retryUntil.value = Date.now() + seconds * 1000
  statusMessage.value = `Limite de consultas atingido. Aguarde ${seconds} s para consultar novamente.${requestId ? ` Referência: ${requestId}` : ''}`
  const update = () => {
    cooldownSeconds.value = Math.max(0, Math.ceil((retryUntil.value - Date.now()) / 1000))
    if (cooldownSeconds.value === 0) {
      clearCooldown()
      statusRole.value = 'status'
      statusMessage.value = 'Você já pode consultar novamente. Use o botão Consultar previsão.'
    }
  }
  update()
  if (cooldownSeconds.value > 0) retryTimer = setInterval(update, 1000)
}

function showError(caught: unknown, form: QueryFormState) {
  statusRole.value = 'alert'
  if (caught instanceof QueryTimeoutError || timedOut.value) {
    statusMessage.value = 'A consulta demorou mais que o esperado. Tente novamente.'
    return
  }
  if (!(caught instanceof QueryError)) {
    statusMessage.value = 'Não foi possível concluir a consulta. Tente novamente.'
    return
  }
  if (caught.status === 429) {
    updateCooldown(caught.requestId, caught.retryAfter)
    return
  }
  let message = 'Não foi possível concluir a consulta. Tente novamente.'
  let field: string | undefined
  if (caught.code === 'NETWORK_ERROR') message = 'Verifique sua conexão e tente novamente.'
  else if (caught.code !== 'MALFORMED_RESPONSE') {
    if (caught.status === 404) {
      message = 'Local não encontrado. Inclua o estado ou país, ou confira as coordenadas.'
      field = form.locationMode === 'city' ? 'location_text' : 'latitude'
    } else if (caught.status === 422) {
      if (caught.code === 'INVALID_PERIOD') {
        message = 'Revise o período: use de 1 a 7 dias, com a data final igual ou posterior à inicial.'
        field = form.endDate ? 'end_date' : 'start_date'
      } else if (caught.code === 'INVALID_TEMPERATURE_UNIT') {
        message = 'Revise a unidade de temperatura e consulte novamente.'
        field = 'temperature_unit'
      } else {
        message = 'Revise a cidade ou o par de coordenadas e consulte novamente.'
        field = form.locationMode === 'city' ? 'location_text' : 'latitude'
      }
    } else if (caught.status === 502 || caught.status === 503) {
      message = 'Previsão indisponível no momento. Tente novamente em instantes.'
    }
  }
  statusMessage.value = `${message}${caught.requestId ? ` Referência: ${caught.requestId}` : ''}`
  if (field) formRef.value?.setFieldError(field, message)
}

async function runQuery(form: QueryFormState) {
  if (cooldownSeconds.value > 0) return
  clearCooldown()
  statusRole.value = 'status'
  statusMessage.value = 'Consultando a previsão… Você pode cancelar ou enviar outra consulta.'
  const response = await submit({
    start_date: form.startDate,
    temperature_unit: form.temperatureUnit,
    ...(form.locationMode === 'city'
      ? { location_text: form.locationText.trim() }
      : { latitude: Number(form.latitude), longitude: Number(form.longitude) }),
    ...(form.endDate ? { end_date: form.endDate } : {}),
  })
  if (response) {
    statusRole.value = 'status'
    statusMessage.value = `Previsão recebida para ${response.location.name}. Confira a qualidade dos dados abaixo.`
  } else if (error.value) {
    showError(error.value, form)
  }
}

function onInvalid() {
  statusRole.value = 'alert'
  statusMessage.value = 'Revise os campos indicados para consultar.'
}

function onCancel() {
  cancel()
  statusRole.value = 'status'
  statusMessage.value = 'Consulta cancelada. Você pode consultar novamente.'
}

function onLocationSelected(candidate: LocationCandidate) {
  statusRole.value = 'status'
  statusMessage.value = `Localidade selecionada: ${candidate.name}. Confirme e consulte.`
}

onBeforeUnmount(clearCooldown)
</script>

<template>
  <a class="skip-link" href="#consulta">Ir para a consulta</a>
  <header class="masthead">
    <a class="brand" href="/" aria-label="Clima Prev, início"><span class="brand-mark" aria-hidden="true"><svg class="yin-yang-logo" viewBox="0 0 40 40" focusable="false"><circle cx="20" cy="20" r="18" fill="var(--earth-green)" /><path d="M20 2a18 18 0 0 1 0 36 9 9 0 0 1 0-18 9 9 0 0 0 0-18Z" fill="var(--earth-blue)" /><circle cx="20" cy="11" r="2.5" fill="var(--earth-green)" /><circle cx="20" cy="29" r="2.5" fill="var(--earth-blue)" /></svg></span> clima prev<span class="brand-dot">.</span></a>
    <div class="masthead-tools">
      <span class="masthead-note">TEMPO · DADOS · CONTEXTO</span>
      <button
        class="theme-toggle"
        type="button"
        :aria-pressed="isDark"
        :aria-label="isDark ? 'Modo escuro ativo. Ativar modo claro' : 'Modo claro ativo. Ativar modo escuro'"
        @click="toggleTheme"
      >
        <span class="theme-toggle-track" aria-hidden="true"><span class="theme-toggle-thumb">{{ isDark ? '☾' : '☀' }}</span></span>
        <span class="theme-toggle-text">{{ isDark ? 'Escuro' : 'Claro' }}</span>
      </button>
    </div>
  </header>
  <main>
    <section class="intro" aria-labelledby="page-title">
      <p class="eyebrow">SEU PRÓXIMO DIA, MAIS CLARO</p>
      <h1 id="page-title">O tempo muda.<br /><em>Planeje com contexto.</em></h1>
      <p class="intro-copy">Veja a previsão e os sinais de risco para o seu local. Entenda o que os dados dizem e o que ainda falta saber.</p>
    </section>
    <section id="consulta" class="query-section" aria-labelledby="query-heading" tabindex="-1">
      <div class="section-heading"><span class="section-number" aria-hidden="true">01</span><h2 id="query-heading">Sua consulta</h2><span class="section-note">Até 7 dias por vez</span></div>
      <QueryForm ref="formRef" :loading="loading" :cooldown-seconds="cooldownSeconds" @submit="runQuery" @cancel="onCancel" @invalid="onInvalid" @selected="onLocationSelected" />
      <QueryStatus :message="statusMessage" :role="statusRole" :show-result="hasResult" :cooldown-seconds="cooldownSeconds" />
    </section>
    <ForecastResult v-if="hasResult && result" :data="result" />
    <aside class="context-note"><span aria-hidden="true">↳</span><div><h2>Previsão é orientação, não certeza.</h2><p>A estimativa de risco ajuda a interpretar a previsão. Ela não substitui uma avaliação local nem os alertas das autoridades.</p></div></aside>
  </main>
  <footer><span>clima prev.</span><p>Consulta anônima · Sem histórico de localização</p></footer>
</template>
