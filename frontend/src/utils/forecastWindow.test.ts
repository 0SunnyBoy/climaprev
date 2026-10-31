import { expect, it } from 'vitest'
import { forecastWindow } from './forecastWindow'

it('uses UTC at opposite local dates and crosses the year boundary', () => {
  expect(forecastWindow(new Date('2026-10-20T23:30:00-03:00'))).toEqual({ first: '2026-10-21', last: '2026-11-03' })
  expect(forecastWindow(new Date('2026-10-21T00:30:00+14:00'))).toEqual({ first: '2026-10-20', last: '2026-11-02' })
  expect(forecastWindow(new Date('2026-12-31T23:59:59Z'))).toEqual({ first: '2026-12-31', last: '2027-01-13' })
  expect(forecastWindow(new Date('2026-12-31T23:59:59Z'), 14)).toEqual({ first: '2026-12-31', last: '2027-01-13' })
})
