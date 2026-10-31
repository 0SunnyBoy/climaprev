import { mount, shallowMount, flushPromises } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import App from './App.vue'
import QueryForm from '@/components/QueryForm.vue'
import QueryStatus from '@/components/QueryStatus.vue'
import { useLocale } from '@/composables/useLocale'
import { emptyQueryForm } from '@/types/query'
import { QueryError } from '@/services/api'

const query = vi.hoisted(() => ({ submit: vi.fn(), failure: null as unknown, previous: null as unknown }))
vi.mock('@/composables/useRiskQuery', async () => {
  const { ref } = await import('vue')
  return { useRiskQuery: () => ({ result: ref(query.previous), loading: ref(false),
    timedOut: ref(false), error: ref(query.failure), submit: query.submit, cancel: vi.fn() }) }
})

describe('idioma da consulta já recebida', () => {
  it('não repete o alerta 429 a cada segundo e anuncia quando a espera termina', async () => {
    vi.useFakeTimers()
    const { setLocale, t } = useLocale()
    setLocale('pt-BR')
    query.failure = new QueryError('RATE_LIMITED', { status: 429, retryAfter: 3, requestId: 'synthetic-id' })
    query.submit.mockResolvedValue(null)
    const wrapper = mount(App)
    try {
      wrapper.findComponent(QueryForm).vm.$emit('submit', emptyQueryForm())
      await vi.advanceTimersByTimeAsync(0)
      const initialMessage = wrapper.get('#query-status').text()
      expect(initialMessage).toContain('3 s.')
      expect(wrapper.get('#query-status').attributes('role')).toBe('alert')
      expect(wrapper.get('.cooldown-countdown').attributes('aria-live')).toBe('off')
      await vi.advanceTimersByTimeAsync(1000)
      expect(wrapper.get('#query-status').text()).toBe(initialMessage)
      expect(wrapper.get('.cooldown-countdown').text()).toContain('2 s')
      setLocale('en')
      await vi.advanceTimersByTimeAsync(0)
      expect(wrapper.get('#query-status').text()).toBe(`${t('rateLimitWait')} 3 s. ${t('reference')}: synthetic-id`)
      await vi.advanceTimersByTimeAsync(2000)
      expect(wrapper.get('#query-status').text()).toBe(t('readyToQuery'))
      expect(wrapper.get('#query-status').attributes('role')).toBe('status')
      expect(wrapper.find('.cooldown-countdown').exists()).toBe(false)
      expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeUndefined()
      expect(query.submit).toHaveBeenCalledTimes(1)
    } finally {
      wrapper.unmount()
      vi.useRealTimers()
      query.failure = null
      query.submit.mockReset()
      setLocale('pt-BR')
    }
  })
  it('traduz também o erro associado ao campo após resposta 422', async () => {
    const { setLocale, t } = useLocale()
    setLocale('pt-BR')
    query.failure = new QueryError('INVALID_PERIOD', { status: 422 })
    query.submit.mockResolvedValue(null)
    const wrapper = mount(App, { attachTo: document.body })
    try {
      wrapper.findComponent(QueryForm).vm.$emit('submit', emptyQueryForm())
      await flushPromises()
      expect(wrapper.get('#start-date-error').text()).toBe(t('invalidPeriod'))
      setLocale('en')
      await flushPromises()
      expect(wrapper.get('#start-date-error').text()).toBe(t('invalidPeriod'))
    } finally {
      wrapper.unmount()
      query.failure = null
      query.submit.mockReset()
      setLocale('pt-BR')
    }
  })
  it('traduz erro já exibido e sua referência sem repetir a consulta', async () => {
    const { setLocale, t } = useLocale()
    setLocale('pt-BR')
    query.failure = new QueryError('WEATHER_PROVIDER_UNAVAILABLE', { status: 503, requestId: 'synthetic-id' })
    query.submit.mockResolvedValue(null)
    const wrapper = shallowMount(App)
    try {
      wrapper.findComponent(QueryForm).vm.$emit('submit', emptyQueryForm())
      await flushPromises()
      expect(wrapper.findComponent(QueryStatus).props('message')).toContain('Referência: synthetic-id')
      setLocale('en')
      await flushPromises()
      expect(wrapper.findComponent(QueryStatus).props('message')).toBe(`${t('forecastUnavailable')} Reference: synthetic-id`)
      expect(query.submit).toHaveBeenCalledTimes(1)
    } finally {
      wrapper.unmount()
      query.failure = null
      query.submit.mockReset()
      setLocale('pt-BR')
    }
  })

  it('preserva formulário e resultado ao voltar da emergência e move o foco', async () => {
    window.history.replaceState(null, '', '/')
    query.previous = { location: { name: 'Belém' } }
    const wrapper = mount(App, { attachTo: document.body, global: { stubs: { ForecastResult: true } } })
    try {
      await wrapper.get('#location-mode').setValue('coordinates')
      await wrapper.get('#latitude').setValue('-1.4558')
      await wrapper.get('#longitude').setValue('-48.4902')
      await wrapper.get('#start_date').setValue('2026-10-20')
      const originalForm = wrapper.get('#query-form').element
      window.history.replaceState(null, '', '/#emergencia')
      window.dispatchEvent(new HashChangeEvent('hashchange'))
      await flushPromises()
      expect(document.activeElement?.id).toBe('emergencia')
      expect(wrapper.get('.home-page').isVisible()).toBe(false)
      window.history.replaceState(null, '', '/#consulta')
      window.dispatchEvent(new HashChangeEvent('hashchange'))
      await flushPromises()
      expect(wrapper.get('#query-form').element).toBe(originalForm)
      expect(wrapper.get<HTMLInputElement>('#latitude').element.value).toBe('-1.4558')
      expect(wrapper.get<HTMLInputElement>('#start_date').element.value).toBe('2026-10-20')
      expect(wrapper.findComponent({ name: 'ForecastResult' }).exists()).toBe(true)
      expect(document.activeElement?.id).toBe('consulta')
    } finally {
      wrapper.unmount()
      query.previous = null
      window.history.replaceState(null, '', '/')
    }
  })
  it('traduz a mensagem existente sem repetir a requisição', async () => {
    const { setLocale, t } = useLocale()
    setLocale('pt-BR')
    query.submit.mockResolvedValue({ location: { name: 'Belém' } })
    const wrapper = shallowMount(App)
    try {
      wrapper.findComponent(QueryForm).vm.$emit('submit', emptyQueryForm())
      await flushPromises()
      expect(wrapper.findComponent(QueryStatus).props('message')).toContain(t('queryReceived'))
      setLocale('en')
      await flushPromises()
      expect(wrapper.findComponent(QueryStatus).props('message')).toBe(
        `${t('queryReceived')} Belém. ${t('checkDataQuality')}`,
      )
      expect(query.submit).toHaveBeenCalledTimes(1)
    } finally {
      wrapper.unmount()
      setLocale('pt-BR')
      query.submit.mockReset()
    }
  })
})
