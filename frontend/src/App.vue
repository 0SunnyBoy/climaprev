<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import EmergencyPage from '@/components/EmergencyPage.vue'
import ForecastResult from '@/components/ForecastResult.vue'
import QueryForm from '@/components/QueryForm.vue'
import QueryStatus from '@/components/QueryStatus.vue'
import { QueryError, QueryTimeoutError } from '@/services/api'
import { useRiskQuery } from '@/composables/useRiskQuery'
import { useLocale, type MessageKey } from '@/composables/useLocale'
import { useTheme } from '@/composables/useTheme'
import type { LocationCandidate } from '@/types/api'
import { toRiskQueryPayload, type QueryFormState } from '@/types/query'

const formRef = ref<{ setFieldError: (name: string, message: string | (() => string)) => void } | null>(null)
const statusMessage = ref<string | (() => string)>('')
const renderedStatusMessage = computed(() => typeof statusMessage.value === 'function'
  ? statusMessage.value() : statusMessage.value)
const statusRole = ref<'status' | 'alert'>('status')
const retryUntil = ref(0)
const cooldownSeconds = ref(0)
let retryTimer: ReturnType<typeof setInterval> | undefined

const { result, loading, timedOut, error, submit, cancel } = useRiskQuery()
const { isDark, toggleTheme } = useTheme()
const { locale, isEnglish, t, toggleLocale } = useLocale()
const hasResult = computed(() => result.value !== null)
type AppPage = 'home' | 'emergency'

function pageFromHash(): AppPage {
  return typeof window !== 'undefined' && window.location.hash === '#emergencia' ? 'emergency' : 'home'
}

const page = ref<AppPage>(pageFromHash())

function updateDocumentMetadata() {
  if (typeof document === 'undefined') return
  document.title = page.value === 'emergency'
    ? `${t('emergencyTitle')} · ClimaPrev`
    : t('homeDocumentTitle')
}

function syncPage() {
  const nextPage = pageFromHash()
  if (nextPage === 'emergency' && page.value !== nextPage && loading.value) onCancel()
  page.value = nextPage
  updateDocumentMetadata()
}

function goHome(event: MouseEvent) {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
  event.preventDefault()
  if (page.value === 'emergency') {
    window.location.hash = '#consulta'
    return
  }
  window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`)
  window.scrollTo({ top: 0, behavior: 'auto' })
}

function clearCooldown() {
  if (retryTimer) clearInterval(retryTimer)
  retryTimer = undefined
  cooldownSeconds.value = 0
}

function updateCooldown(requestId: string, seconds: number) {
  clearCooldown()
  retryUntil.value = Date.now() + seconds * 1000
  statusMessage.value = () => `${t('rateLimitWait')} ${seconds} s.${requestId ? ` ${t('reference')}: ${requestId}` : ''}`
  const update = () => {
    cooldownSeconds.value = Math.max(0, Math.ceil((retryUntil.value - Date.now()) / 1000))
    if (cooldownSeconds.value === 0) {
      clearCooldown()
      statusRole.value = 'status'
      statusMessage.value = () => t('readyToQuery')
    }
  }
  update()
  if (cooldownSeconds.value > 0) retryTimer = setInterval(update, 1000)
}

function showError(caught: unknown, form: QueryFormState) {
  statusRole.value = 'alert'
  if (caught instanceof QueryTimeoutError || timedOut.value) {
    statusMessage.value = () => t('queryTimeout')
    return
  }
  if (!(caught instanceof QueryError)) {
    statusMessage.value = () => t('genericQueryError')
    return
  }
  if (caught.status === 429) {
    updateCooldown(caught.requestId, caught.retryAfter)
    return
  }
  let messageKey: MessageKey = 'genericQueryError'
  let field: string | undefined
  if (caught.code === 'NETWORK_ERROR') messageKey = 'networkError'
  else if (caught.code !== 'MALFORMED_RESPONSE') {
    if (caught.status === 404) {
      messageKey = 'locationNotFound'
      field = form.locationMode === 'city' ? 'location_text' : 'latitude'
    } else if (caught.status === 422) {
      if (caught.code === 'INVALID_PERIOD') {
        messageKey = 'invalidPeriod'
        field = form.endDate ? 'end_date' : 'start_date'
      } else if (caught.code === 'INVALID_TEMPERATURE_UNIT') {
        messageKey = 'invalidTemperature'
        field = 'temperature_unit'
      } else {
        messageKey = 'invalidLocation'
        field = form.locationMode === 'city' ? 'location_text' : 'latitude'
      }
    } else if (caught.status === 502 || caught.status === 503) {
      messageKey = 'forecastUnavailable'
    }
  }
  statusMessage.value = () => `${t(messageKey)}${caught.requestId ? ` ${t('reference')}: ${caught.requestId}` : ''}`
  if (field) formRef.value?.setFieldError(field, () => t(messageKey))
}

async function runQuery(form: QueryFormState) {
  if (cooldownSeconds.value > 0) return
  clearCooldown()
  statusRole.value = 'status'
  statusMessage.value = () => t('querying')
  const response = await submit(toRiskQueryPayload(form))
  if (response) {
    statusRole.value = 'status'
    statusMessage.value = () => `${t('queryReceived')} ${response.location.name}. ${t('checkDataQuality')}`
  } else if (error.value) {
    showError(error.value, form)
  }
}

function onInvalid() {
  statusRole.value = 'alert'
  statusMessage.value = () => t('invalidForm')
}

function onCancel() {
  cancel()
  statusRole.value = 'status'
  statusMessage.value = () => t('queryCancelled')
}

function onLocationSelected(candidate: LocationCandidate) {
  statusRole.value = 'status'
  statusMessage.value = () => `${t('locationSelected')}: ${candidate.name}. ${t('confirmAndQuery')}`
}

watch([page, locale], updateDocumentMetadata)
watch(page, async () => {
  await nextTick()
  document.getElementById(page.value === 'emergency' ? 'emergencia' : 'consulta')?.focus()
})

onMounted(() => window.addEventListener('hashchange', syncPage))
onMounted(updateDocumentMetadata)

onBeforeUnmount(() => {
  clearCooldown()
  window.removeEventListener('hashchange', syncPage)
})
</script>

<template>
  <a class="skip-link" :href="page === 'emergency' ? '#emergencia' : '#consulta'">{{ page === 'emergency' ? t('emergencyTitle') : t('skipToQuery') }}</a>
  <header class="masthead">
    <a class="brand" href="/" :aria-label="t('brandAria')" @click="goHome"><span class="brand-mark" aria-hidden="true"><svg class="yin-yang-logo" viewBox="0 0 40 40" focusable="false"><circle cx="20" cy="20" r="18" fill="var(--earth-green)" /><path d="M20 2a18 18 0 0 1 0 36 9 9 0 0 1 0-18 9 9 0 0 0 0-18Z" fill="var(--earth-blue)" /><circle cx="20" cy="11" r="2.5" fill="var(--earth-green)" /><circle cx="20" cy="29" r="2.5" fill="var(--earth-blue)" /></svg></span> ClimaPrev<span class="brand-dot">.</span></a>
    <div class="masthead-tools">
      <span class="masthead-note">{{ t('navigationNote') }}</span>
      <a class="emergency-nav-link" href="#emergencia" :aria-current="page === 'emergency' ? 'page' : undefined">{{ t('emergencyNav') }}</a>
      <button class="locale-toggle" type="button" :aria-label="t('languageLabel')" @click="toggleLocale">
        <span :class="{ 'locale-active': locale === 'pt-BR' }">PT-BR</span>
        <span aria-hidden="true"> / </span>
        <span :class="{ 'locale-active': isEnglish }">EN</span>
      </button>
      <button
        class="theme-toggle"
        type="button"
        :aria-pressed="isDark"
        :aria-label="isDark ? t('themeDarkActive') : t('themeLightActive')"
        @click="toggleTheme"
      >
        <span class="theme-toggle-track" aria-hidden="true"><span class="theme-toggle-thumb">{{ isDark ? '☾' : '☀' }}</span></span>
        <span class="theme-toggle-text">{{ isDark ? t('dark') : t('light') }}</span>
      </button>
    </div>
  </header>
  <main>
    <div v-show="page === 'home'" class="home-page">
      <section class="intro" aria-labelledby="page-title">
        <p class="eyebrow">{{ t('homeEyebrow') }}</p>
        <h1 id="page-title">{{ t('homeTitleFirst') }}<br /><em>{{ t('homeTitleSecond') }}</em></h1>
        <p class="intro-copy">{{ t('homeIntro') }}</p>
      </section>
      <section id="consulta" class="query-section" aria-labelledby="query-heading" tabindex="-1">
        <div class="section-heading"><h2 id="query-heading">{{ t('queryTitle') }}</h2><span class="section-note">{{ t('queryLimit') }}</span></div>
        <QueryForm ref="formRef" :loading="loading" :cooldown-seconds="cooldownSeconds" @submit="runQuery" @cancel="onCancel" @invalid="onInvalid" @selected="onLocationSelected" />
        <QueryStatus :message="renderedStatusMessage" :role="statusRole" :show-result="hasResult" :cooldown-seconds="cooldownSeconds" />
      </section>
      <ForecastResult v-if="hasResult && result" :data="result" />
      <aside class="context-note"><span aria-hidden="true">↳</span><div><h2>{{ t('contextTitle') }}</h2><p>{{ t('contextBody') }}</p></div></aside>
    </div>
    <EmergencyPage v-if="page === 'emergency'" />
  </main>
  <footer><span>ClimaPrev<span class="brand-dot">.</span></span><p>{{ t('anonymous') }}</p></footer>
</template>
