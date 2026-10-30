import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import RiskSummary from './RiskSummary.vue'
import OfficialAlerts from './OfficialAlerts.vue'
import { useLocale, type MessageKey } from '@/composables/useLocale'
import type { ForecastRisk, RiskCondition } from '@/types/api'

const conditions: RiskCondition[] = [
  { type: 'heavy_rain_proxy', severity: 'high', value: 50, unit: 'mm/day', reason: 'Indicador de chuva, não alerta oficial.' },
  { type: 'flooding_risk_proxy', severity: 'high', value: 50, unit: 'mm/day', reason: 'Sinal de alagamento, não avaliação hidrológica.' },
  { type: 'strong_wind_proxy', severity: 'high', value: 61, unit: 'km/h', reason: 'Indicador de vento, não alerta oficial.' },
  { type: 'temperature_extreme_proxy', severity: 'high', value: 40, unit: 'celsius', reason: 'Indicador de calor, não onda de calor.' },
  { type: 'temperature_extreme_proxy', severity: 'high', value: 0, unit: 'celsius', reason: 'Indicador de frio, não alerta oficial.' },
]
const labels: Record<string, MessageKey> = {
  heavy_rain_proxy: 'conditionHeavyRain', flooding_risk_proxy: 'conditionFlooding',
  strong_wind_proxy: 'conditionStrongWind', temperature_extreme_proxy: 'conditionExtremeTemperature',
}

function risk(items: RiskCondition[]): ForecastRisk {
  return { level: 'high', method: 'forecast_heuristic', policy_version: 'reference-v1',
    conditions: items, daily: [], peak_days: ['2026-08-28'] }
}

afterEach(() => useLocale().setLocale('pt-BR'))

describe('entrega de todas as condições de risco à tela', () => {
  for (const locale of ['pt-BR', 'en'] as const) {
    it.each(conditions)(`exibe $type de valor $value em ${locale}`, (condition) => {
      const { setLocale, t } = useLocale()
      setLocale(locale)
      const wrapper = mount(RiskSummary, { props: { risk: risk([condition]),
        overview: { level: 'high', source: 'forecast_heuristic', peak_days: ['2026-08-28'] },
        completeness: 'complete' } })
      try {
        expect(wrapper.findAll('.conditions li')).toHaveLength(1)
        expect(wrapper.get('.conditions strong').text()).not.toContain(condition.type)
        expect(wrapper.get('.conditions strong').text()).toContain(t(labels[condition.type]!))
        expect(wrapper.get('.conditions strong').text()).toContain(String(condition.value))
        expect(wrapper.get('.conditions p').text().length).toBeGreaterThan(10)
        if (condition.unit === 'celsius') expect(wrapper.get('.conditions strong').text()).toContain('°C')
      } finally { wrapper.unmount() }
    })
  }

  it('preserva condições simultâneas e dados parciais mesmo com prioridade oficial', () => {
    const wrapper = mount(RiskSummary, { props: { risk: risk(conditions.slice(0, 4)),
      overview: { level: 'high', source: 'official_alert', peak_days: ['2026-08-28'] },
      completeness: 'partial' } })
    try {
      expect(wrapper.findAll('.conditions li')).toHaveLength(4)
      expect(wrapper.get('.official-priority').text()).toBe(useLocale().t('officialRiskPriority'))
      expect(wrapper.get('.quality-warning').text()).toBe(useLocale().t('incompleteData'))
    } finally { wrapper.unmount() }
  })

  it('exibe a unidade Fahrenheit recebida da API sem alterar o valor', () => {
    const condition = { ...conditions[3]!, value: 104, unit: 'fahrenheit' }
    const wrapper = mount(RiskSummary, { props: { risk: risk([condition]),
      overview: { level: 'high', source: 'forecast_heuristic', peak_days: [] },
      completeness: 'complete' } })
    try {
      expect(wrapper.get('.conditions strong').text()).toContain('104 °F')
    } finally { wrapper.unmount() }
  })

  it('não apresenta condições como confiáveis quando todos os dados estão indisponíveis', () => {
    const wrapper = mount(RiskSummary, { props: { risk: risk([]),
      overview: { level: 'low', source: 'forecast_heuristic', peak_days: [] },
      completeness: 'unavailable' } })
    try {
      expect(wrapper.find('.conditions').exists()).toBe(false)
      expect(wrapper.find('.risk-level').exists()).toBe(false)
      expect(wrapper.get('.quality-warning').text()).toBe(useLocale().t('insufficientData'))
    } finally { wrapper.unmount() }
  })

  it.each(['available', 'unavailable'] as const)('distingue o estado oficial %s da estimativa', (status) => {
    const { t } = useLocale()
    const wrapper = mount(OfficialAlerts, { props: { alerts: { status, items: [] }, timezone: 'UTC' } })
    try {
      expect(wrapper.text()).toContain(t(status === 'available' ? 'noAlerts' : 'alertsUnavailable'))
      expect(wrapper.find('article').exists()).toBe(false)
    } finally { wrapper.unmount() }
  })
})

describe('apresentação da estratégia candidata aceita', () => {
  for (const locale of ['pt-BR', 'en'] as const) {
    it.each([
      { unit: 'celsius', value: 40, label: '40 °C' },
      { unit: 'fahrenheit', value: 104, label: '104 °F' },
    ])(`preserva $label e texto de risco em ${locale}`, ({ unit, value, label }) => {
      const { setLocale, t } = useLocale()
      setLocale(locale)
      const candidate = { ...risk([{ ...conditions[3]!, unit, value }]), policy_version: 'reference-candidate-1' }
      const wrapper = mount(RiskSummary, { props: { risk: candidate,
        overview: { level: 'high', source: 'forecast_heuristic', peak_days: [] }, completeness: 'complete' } })
      try {
        expect(wrapper.get('.conditions strong').text()).toContain(label)
        expect(wrapper.get('.risk-level').text()).toBe(t('riskHigh'))
        expect(wrapper.get('.quality-line').text()).toBe(t('completeData'))
        expect(wrapper.text()).not.toMatch(/confidence|confiança|MAE|bootstrap|95%/i)
      } finally { wrapper.unmount() }
    })

    it(`mantém alerta oficial prioritário e avisa sobre dados parciais em ${locale}`, () => {
      const { setLocale, t } = useLocale()
      setLocale(locale)
      const candidate = { ...risk([]), level: 'low' as const, policy_version: 'reference-candidate-1' }
      const wrapper = mount(RiskSummary, { props: { risk: candidate,
        overview: { level: 'high', source: 'official_alert', peak_days: [] }, completeness: 'partial' } })
      try {
        expect(wrapper.get('.risk-level').text()).toBe(t('riskHigh'))
        expect(wrapper.get('.official-priority').text()).toBe(t('officialRiskPriority'))
        expect(wrapper.get('.quality-warning').text()).toBe(t('incompleteData'))
      } finally { wrapper.unmount() }
    })

    it(`preserva ausência de dados sem inventar confiança em ${locale}`, () => {
      const { setLocale, t } = useLocale()
      setLocale(locale)
      const candidate = { ...risk([]), policy_version: 'reference-candidate-1' }
      const wrapper = mount(RiskSummary, { props: { risk: candidate,
        overview: { level: 'low', source: 'forecast_heuristic', peak_days: [] }, completeness: 'unavailable' } })
      try {
        expect(wrapper.get('.quality-warning').text()).toBe(t('insufficientData'))
        expect(wrapper.find('.risk-level').exists()).toBe(false)
        expect(wrapper.find('.conditions').exists()).toBe(false)
        expect(wrapper.text()).not.toMatch(/confidence|confiança|MAE|bootstrap|95%/i)
      } finally { wrapper.unmount() }
    })
  }
})
