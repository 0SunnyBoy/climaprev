/** UTC controls request eligibility; forecast day aggregation keeps location timezone. */
export function forecastWindow(now = new Date(), horizonDays = 7): { first: string; last: string } {
  if (!Number.isInteger(horizonDays) || horizonDays < 1 || horizonDays > 16) {
    throw new Error('Unsupported forecast horizon')
  }
  const first = now.toISOString().slice(0, 10)
  const last = new Date(`${first}T00:00:00Z`)
  last.setUTCDate(last.getUTCDate() + horizonDays - 1)
  return { first, last: last.toISOString().slice(0, 10) }
}
