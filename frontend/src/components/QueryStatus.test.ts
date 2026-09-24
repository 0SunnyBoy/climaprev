import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import QueryStatus from './QueryStatus.vue'

describe('aviso de limite de consultas', () => {
  it('mantém a contagem visual fora da região de alerta', async () => {
    const message = 'Limite de consultas atingido. Aguarde 3 s para consultar novamente.'
    const wrapper = mount(QueryStatus, {
      props: { message, role: 'alert', showResult: false, cooldownSeconds: 3 },
    })

    expect(wrapper.get('#query-status').attributes('role')).toBe('alert')
    expect(wrapper.get('#query-status').text()).toBe(message)
    expect(wrapper.get('.cooldown-countdown').text()).toBe('Tempo restante: 3 s')
    expect(wrapper.get('#query-status').element.contains(wrapper.get('.cooldown-countdown').element)).toBe(false)

    await wrapper.setProps({ cooldownSeconds: 2 })
    expect(wrapper.get('#query-status').text()).toBe(message)
    expect(wrapper.get('.cooldown-countdown').text()).toBe('Tempo restante: 2 s')

    await wrapper.setProps({
      message: 'Você já pode consultar novamente. Use o botão Consultar previsão.',
      role: 'status',
      cooldownSeconds: 0,
    })
    expect(wrapper.get('#query-status').attributes('role')).toBe('status')
    expect(wrapper.find('.cooldown-countdown').exists()).toBe(false)
  })
})
