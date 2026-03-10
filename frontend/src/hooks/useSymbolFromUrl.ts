import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'

export function useSymbolFromUrl(): { symbol: string | null; error: string | null } {
  const { symbol: param } = useParams<{ symbol: string }>()
  const [error, setError] = useState<string | null>(null)
  const symbol = (param || '').trim().toUpperCase() || null

  useEffect(() => {
    if (!symbol) {
      setError(null)
      return
    }
    setError(null)
    // Validation will happen when we fetch (backend returns 404 for invalid)
  }, [symbol])

  if (!param) return { symbol: null, error: null }
  return { symbol: symbol || null, error }
}
