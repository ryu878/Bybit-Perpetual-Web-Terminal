const API_BASE = '/api'

function messageFromDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (first && typeof first === 'object' && 'msg' in first) return String((first as { msg?: unknown }).msg ?? JSON.stringify(detail))
    return JSON.stringify(detail)
  }
  if (detail && typeof detail === 'object') return JSON.stringify(detail)
  return ''
}

export async function apiGet<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, window.location.origin)
  url.pathname = API_BASE + path
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }
  const res = await fetch(url.toString())
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const detail = (body as { detail?: unknown }).detail
    throw new Error(messageFromDetail(detail) || res.statusText)
  }
  return res.json()
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const detail = (data as { detail?: unknown }).detail
    throw new Error(messageFromDetail(detail) || res.statusText)
  }
  return res.json()
}
