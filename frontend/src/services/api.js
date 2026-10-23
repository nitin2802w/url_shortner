const API_BASE = 'http://localhost:8000'

/**
 * POST /api/v1/shorten
 * Shorten a long URL, with an optional custom alias.
 */
export async function shortenUrl(longUrl, customAlias = null) {
  const body = { long_url: longUrl }
  if (customAlias && customAlias.trim()) body.custom_alias = customAlias.trim()

  const res = await fetch(`${API_BASE}/api/v1/shorten`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  const data = await res.json()
  if (!res.ok) throw data   // { detail: "..." }
  return data
  // { short_url, short_code, long_url, custom_alias, clicks, created_at }
}

/**
 * GET /api/v1/stats/:shortCode
 * Fetch stats for a given short code (Module 5 endpoint).
 */
export async function getStats(shortCode) {
  const res = await fetch(`${API_BASE}/api/v1/stats/${shortCode}`)
  const data = await res.json()
  if (!res.ok) throw data
  return data
}
