import { useRef, useEffect, useMemo } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts'
import type { CandleItem, PositionItem } from '../types/api'

interface ChartPanelProps {
  symbol: string
  timeframe: string
  candles: CandleItem[]
  positions?: PositionItem[]
}

export default function ChartPanel({ symbol, timeframe, candles, positions = [] }: ChartPanelProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const positionLinesRef = useRef<ReturnType<ISeriesApi<'Candlestick'>['createPriceLine']>[]>([])

  const candleData = useMemo((): CandlestickData[] => {
    const raw = candles.map((c) => {
      const t = typeof c.time === 'number' ? c.time : Math.floor(Number(c.time) / (Number(c.time) > 1e12 ? 1000 : 1))
      return {
        time: t,
        open: parseFloat(String(c.open)) || 0,
        high: parseFloat(String(c.high)) || 0,
        low: parseFloat(String(c.low)) || 0,
        close: parseFloat(String(c.close)) || 0,
      } as CandlestickData
    })
    return raw.sort((a, b) => (a.time as number) - (b.time as number))
  }, [candles])

  useEffect(() => {
    const container = containerRef.current
    if (!container || !candleData.length) return
    const w = container.clientWidth || 800
    const h = container.clientHeight || 400
    if (w <= 0 || h <= 0) return
    let chart: IChartApi
    try {
      chart = createChart(container, {
        layout: { background: { color: '#ffffff' }, textColor: '#374151' },
        grid: { vertLines: { color: '#e5e7eb' }, horzLines: { color: '#e5e7eb' } },
        width: w,
        height: h,
        timeScale: { timeVisible: true, secondsVisible: false },
        rightPriceScale: { borderColor: '#d1d5db' },
      })
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#238636',
        downColor: '#da3633',
        borderDownColor: '#da3633',
        borderUpColor: '#238636',
        priceFormat: {
          type: 'price',
          precision: 8,
          minMove: 0.00000001,
        },
      })
      chartRef.current = chart
      seriesRef.current = candlestickSeries
      return () => {
        try {
          chart.remove()
        } catch {
          // ignore
        }
        chartRef.current = null
        seriesRef.current = null
      }
    } catch (err) {
      console.warn('Chart create:', err)
    }
  }, [symbol, timeframe])

  // Set candle data and position entry lines in one effect so lines are added after data.
  useEffect(() => {
    const series = seriesRef.current
    if (!series || !candleData.length) return
    try {
      series.setData([...candleData])
    } catch (err) {
      console.warn('Chart setData:', err)
    }

    // Remove existing position lines
    const prev = positionLinesRef.current
    prev.forEach((line) => {
      try {
        if (line && typeof (series as { removePriceLine?: (l: unknown) => void }).removePriceLine === 'function') {
          (series as { removePriceLine: (l: unknown) => void }).removePriceLine(line)
        }
      } catch {
        // ignore
      }
    })
    positionLinesRef.current = []

    // Add one horizontal line per position at entry_price
    if (positions.length > 0) {
      const newLines: ReturnType<ISeriesApi<'Candlestick'>['createPriceLine']>[] = []
      for (const p of positions) {
        const entryPriceStr = p.entry_price ?? (p as { entryPrice?: string }).entryPrice ?? ''
        const price = parseFloat(String(entryPriceStr))
        if (!Number.isFinite(price) || price <= 0) continue
        try {
          const line = series.createPriceLine({
            price,
            color: p.side === 'Buy' ? '#238636' : '#da3633',
            lineWidth: 2,
            lineStyle: 0,
            axisLabelVisible: true,
            title: `${p.side} ${p.size}`,
          })
          newLines.push(line)
        } catch (err) {
          console.warn('Chart createPriceLine:', err)
        }
      }
      positionLinesRef.current = newLines
    }

    return () => {
      const ser = seriesRef.current
      if (ser && typeof (ser as { removePriceLine?: (l: unknown) => void }).removePriceLine === 'function') {
        positionLinesRef.current.forEach((line) => {
          try {
            if (line) (ser as { removePriceLine: (l: unknown) => void }).removePriceLine(line)
          } catch {
            // ignore
          }
        })
      }
      positionLinesRef.current = []
    }
  }, [candleData, positions])

  useEffect(() => {
    const chart = chartRef.current
    if (!chart || !containerRef.current) return
    const onResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth })
    }
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  if (!candleData.length) {
    return (
      <div className="chart-panel">
        <div className="chart-panel__placeholder">Loading chart…</div>
      </div>
    )
  }

  const positionEntries = positions
    .map((p) => {
      const entryPriceStr = p.entry_price ?? (p as { entryPrice?: string }).entryPrice ?? ''
      const price = parseFloat(String(entryPriceStr))
      return Number.isFinite(price) && price > 0 ? { side: p.side, size: p.size, price } : null
    })
    .filter((x): x is { side: string; size: string; price: number } => x !== null)

  return (
    <div className="chart-panel chart-panel--with-legend">
      <div className="chart-panel__container" ref={containerRef} style={{ minHeight: '400px' }} />
      {positionEntries.length > 0 && (
        <div className="chart-panel__position-entries">
          {positionEntries.map((e, i) => (
            <span
              key={i}
              className={`chart-panel__position-entry chart-panel__position-entry--${e.side.toLowerCase()}`}
              title={`Entry: ${e.price}`}
            >
              {e.side} {e.size} @ {e.price}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
