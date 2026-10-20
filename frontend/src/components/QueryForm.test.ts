import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import QueryForm from './QueryForm.vue'

describe('acessibilidade do formulário de consulta', () => {
  it('atualiza limites ao cruzar meia-noite UTC e não envia uma data expirada', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-12-31T23:59:59Z'))
    const wrapper = mount(QueryForm, { attachTo: document.body, props: { loading: false, cooldownSeconds: 0 } })
    try {
      expect(wrapper.get('#start_date').attributes('min')).toBe('2026-12-31')
      expect(wrapper.get('#start_date').attributes('max')).toBe('2027-01-06')
      await wrapper.get('#location-mode').setValue('coordinates')
      await wrapper.get('#latitude').setValue('-1')
      await wrapper.get('#longitude').setValue('-48')
      await wrapper.get('#start_date').setValue('2026-12-31')
      await vi.advanceTimersByTimeAsync(30_000)
      expect(wrapper.get('#start_date').attributes('min')).toBe('2027-01-01')
      await wrapper.get('form').trigger('submit')
      expect(wrapper.emitted('submit')).toBeUndefined()
    } finally {
      wrapper.unmount()
      vi.useRealTimers()
    }
  })
  it('associa um erro da API ao campo e move o foco para ele', async () => {
    const wrapper = mount(QueryForm, {
      attachTo: document.body,
      props: { loading: false, cooldownSeconds: 0 },
    })

    try {
      (wrapper.vm as unknown as { setFieldError: (name: string, message: string) => void })
        .setFieldError('location_text', 'Local não encontrado.')
      await nextTick()

      const city = wrapper.get<HTMLInputElement>('#location_text')
      expect(city.attributes('aria-invalid')).toBe('true')
      expect(city.attributes('aria-describedby')).toContain('city-error')
      expect(wrapper.get('#city-error').text()).toBe('Local não encontrado.')
      expect(document.activeElement).toBe(city.element)
    } finally {
      wrapper.unmount()
    }
  })
})
