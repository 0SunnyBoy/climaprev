import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import EmergencyPage from './EmergencyPage.vue'

describe('página de números emergenciais', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.lang = 'pt-BR'
  })

  it('exibe os serviços brasileiros com ações de ligação', () => {
    const wrapper = mount(EmergencyPage)

    expect(wrapper.get('h1').text()).toBe('Números Emergenciais')
    expect(wrapper.get('.emergency-national-notice').text()).toContain('números nacionais do Brasil')
    expect(wrapper.findAll('.emergency-card')).toHaveLength(6)
    expect(wrapper.findAll("a[href^='tel:']")).toHaveLength(6)
    expect(wrapper.get("a[href='tel:193']").attributes('aria-label')).toContain('Corpo de Bombeiros')
    expect(wrapper.text()).toContain('não substitui os serviços oficiais')
  })
})
