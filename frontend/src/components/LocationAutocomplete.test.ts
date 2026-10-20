import { mount, flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import LocationAutocomplete from './LocationAutocomplete.vue'
import { searchLocations } from '@/services/api'

vi.mock('@/services/api', () => ({ searchLocations: vi.fn() }))
afterEach(() => { vi.useRealTimers(); vi.resetAllMocks() })

describe('recuperação da busca de cidades', () => {
  it('limpa aria-activedescendant ao selecionar por teclado e fecha a lista no blur', async () => {
    vi.useFakeTimers()
    vi.mocked(searchLocations).mockResolvedValue([{ name: 'Belém', latitude: -1.4, longitude: -48.4,
      timezone: 'America/Belem', source: 'synthetic' }])
    const wrapper = mount(LocationAutocomplete, { props: { modelValue: 'Belém' } })
    try {
      await wrapper.get('input').trigger('input')
      await vi.advanceTimersByTimeAsync(250)
      await wrapper.get('input').trigger('keydown', { key: 'ArrowDown' })
      expect(wrapper.get('input').attributes('aria-activedescendant')).toBe('location-option-0')
      await wrapper.get('input').trigger('keydown', { key: 'Enter' })
      expect(wrapper.get('input').attributes('aria-activedescendant')).toBeUndefined()
      expect(wrapper.get('input').attributes('aria-expanded')).toBe('false')
      await wrapper.get('input').trigger('input')
      await vi.advanceTimersByTimeAsync(250)
      await wrapper.get('input').trigger('blur')
      expect(wrapper.find('[role="listbox"]').exists()).toBe(false)
    } finally { wrapper.unmount() }
  })
  it('distingue erro de busca vazia e permite repetir', async () => {
    vi.useFakeTimers()
    vi.mocked(searchLocations).mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce([])
    const wrapper = mount(LocationAutocomplete, { props: { modelValue: 'Belém' } })
    try {
      await wrapper.get('input').trigger('input')
      await vi.advanceTimersByTimeAsync(250)
      await flushPromises()
      expect(wrapper.get('[role="status"]#city-search-status').text()).toContain('Não foi possível')
      await wrapper.get('button').trigger('click')
      await vi.advanceTimersByTimeAsync(250)
      await flushPromises()
      expect(wrapper.get('#city-search-status').text()).toContain('Nenhuma cidade')
      expect(wrapper.find('button').exists()).toBe(false)
    } finally { wrapper.unmount() }
  })

  it('ignora falha atrasada de uma busca anterior', async () => {
    vi.useFakeTimers()
    let rejectOld!: (reason: Error) => void
    vi.mocked(searchLocations)
      .mockImplementationOnce(() => new Promise((_, reject) => { rejectOld = reject }))
      .mockResolvedValueOnce([{ name: 'Brasília', latitude: -15.8, longitude: -47.9,
        timezone: 'America/Sao_Paulo', source: 'synthetic' }])
    const wrapper = mount(LocationAutocomplete, { props: { modelValue: 'Belém' } })
    try {
      await wrapper.get('input').trigger('input')
      await vi.advanceTimersByTimeAsync(250)
      await wrapper.get('input').setValue('Brasília')
      await vi.advanceTimersByTimeAsync(250)
      rejectOld(new Error('late failure'))
      await flushPromises()
      expect(wrapper.find('#city-search-status').exists()).toBe(false)
      expect(wrapper.get('[role="option"]').text()).toContain('Brasília')
    } finally { wrapper.unmount() }
  })
})
