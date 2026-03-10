import { useState } from 'react'
import { useSymbolFromUrl } from '../hooks/useSymbolFromUrl'
import { useMarketStream } from '../hooks/useMarketStream'
import { usePositions } from '../hooks/usePositions'
import ChartPanel from '../components/ChartPanel'
import PositionsPanel from '../components/PositionsPanel'
import OrderPanel from '../components/OrderPanel'
import TimeframeSelector from '../components/TimeframeSelector'
import StatusBadge from '../components/StatusBadge'

export default function TerminalPage() {
  const { symbol, error: urlError } = useSymbolFromUrl()
  const [timeframe, setTimeframe] = useState('1m')
  const { candles, error: chartError, status } = useMarketStream(
    symbol || '',
    timeframe
  )
  const { positions, loading: posLoading, error: posError, reload: reloadPositions } = usePositions(
    symbol || ''
  )

  if (urlError) {
    return (
      <div className="terminal terminal--error">
        <p>{urlError}</p>
      </div>
    )
  }

  if (!symbol) {
    return (
      <div className="terminal">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="terminal">
      <header className="terminal__header">
        <span className="terminal__symbol">{symbol}</span>
        <TimeframeSelector value={timeframe} onChange={setTimeframe} />
        <StatusBadge status={status} />
      </header>
      <main className="terminal__main">
        <div className="terminal__chart">
          {chartError && (
            <div className="chart-panel__error">{chartError}</div>
          )}
          <ChartPanel
            symbol={symbol}
            timeframe={timeframe}
            candles={candles}
            positions={positions.filter((p) => p.symbol === symbol)}
          />
        </div>
        <div className="terminal__positions">
          <PositionsPanel
            symbol={symbol}
            positions={positions}
            loading={posLoading}
            error={posError}
          />
        </div>
      </main>
      <aside className="terminal__sidebar">
        <OrderPanel symbol={symbol} onOrderPlaced={reloadPositions} />
      </aside>
    </div>
  )
}
