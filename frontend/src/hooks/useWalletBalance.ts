import { useState, useEffect, useCallback } from 'react'
import { apiGet } from '../api/client'

export interface WalletBalance {
  initial_margin_pct: string
  maintenance_margin_pct: string
  margin_balance: string
  available_balance: string
}

export function useWalletBalance() {
  const [data, setData] = useState<WalletBalance | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiGet<WalletBalance>('/account/wallet-balance')
      setData(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load balance')
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { data, loading, error, reload: load }
}
