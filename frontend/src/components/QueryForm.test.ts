import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import QueryForm from './QueryForm.vue'

describe('acessibilidade do formulário de consulta', () => {
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
