import { useState, useEffect, useCallback } from 'react'
import { apiGet } from '../api/client'
import type { PositionsResponse, PositionItem } from '../types/api'

export function usePositions(_selectedSymbol: string) {
  const [positions, setPositions] = useState<PositionItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiGet<PositionsResponse>('/positions')
      setPositions(data.positions || [])
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to load positions'
      setError(typeof msg === 'string' ? msg : String(msg))
      setPositions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { positions, loading, error, reload: load }
}
