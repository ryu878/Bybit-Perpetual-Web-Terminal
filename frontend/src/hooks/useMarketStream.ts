import { useState, useEffect, useRef, useCallback } from 'react'
import { apiGet } from '../api/client'
import type { CandleItem, MarketHistoryResponse } from '../types/api'

const WS_BASE = (() => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${proto}//${host}/ws`
})()

type WsStatus = 'connected' | 'reconnecting' | 'disconnected'

export function useMarketStream(symbol: string, timeframe: string) {
  const [candles, setCandles] = useState<CandleItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<WsStatus>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const subsRef = useRef({ symbol: '', timeframe: '' })
  const symbolTfRef = useRef({ symbol: symbol.trim().toUpperCase(), timeframe: timeframe.trim().toLowerCase() })
  symbolTfRef.current = { symbol: symbol.trim().toUpperCase(), timeframe: timeframe.trim().toLowerCase() }

  const loadHistory = useCallback(async () => {
    if (!symbol) return
    setLoading(true)
    setError(null)
    try {
      const data = await apiGet<MarketHistoryResponse>('/market/history', {
        symbol,
        timeframe,
        limit: '200',
      })
      setCandles(data.candles || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load history')
      setCandles([])
    } finally {
      setLoading(false)
    }
  }, [symbol, timeframe])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  useEffect(() => {
    if (!symbol || !timeframe) return

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return
      const ws = new WebSocket(WS_BASE)
      wsRef.current = ws

      const sendSubscribe = () => {
        if (ws.readyState !== WebSocket.OPEN) return
        const sym = symbolTfRef.current.symbol
        const tf = symbolTfRef.current.timeframe
        if (!sym || !tf) return
        ws.send(JSON.stringify({ action: 'subscribe', symbol: sym, timeframe: tf }))
      }

      ws.onopen = () => {
        setStatus('connected')
        sendSubscribe()
      }

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data as string)
          if (msg.type === 'status') {
            setStatus('connected')
            return
          }
          if (msg.type !== 'candle' || !msg.data) return
          const msgSymbol = String(msg.symbol || '').trim().toUpperCase()
          const msgTf = String(msg.timeframe || '').trim().toLowerCase()
          const { symbol: curSymbol, timeframe: curTf } = symbolTfRef.current
          if (msgSymbol !== curSymbol || msgTf !== curTf) return
          const d = msg.data
          const newCandle = {
            time: d.time,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
            volume: d.volume ?? '0',
          }
          setCandles((prev) => {
            if (prev.length === 0) return [newCandle]
            const last = prev[prev.length - 1]
            if (last.time === newCandle.time) {
              return [...prev.slice(0, -1), newCandle]
            }
            return [...prev, newCandle]
          })
        } catch {
          // ignore
        }
      }

      ws.onclose = () => {
        wsRef.current = null
        setStatus('disconnected')
        if (subsRef.current.symbol === symbol && subsRef.current.timeframe === timeframe) {
          setStatus('reconnecting')
          reconnectRef.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    subsRef.current = { symbol, timeframe }
    if (reconnectRef.current) {
      clearTimeout(reconnectRef.current)
      reconnectRef.current = null
    }
    let resubscribeInterval: ReturnType<typeof setInterval> | null = null
    connect()
    resubscribeInterval = setInterval(() => {
      const ws = wsRef.current
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'subscribe', symbol: symbol.trim().toUpperCase(), timeframe: timeframe.trim().toLowerCase() }))
      }
    }, 45000)
    return () => {
      if (resubscribeInterval) clearInterval(resubscribeInterval)
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      reconnectRef.current = null
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      setStatus('disconnected')
    }
  }, [symbol, timeframe])

  return { candles, loading, error, status, reload: loadHistory }
}
