import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import type { PositionItem } from '../types/api'

interface PositionsPanelProps {
  symbol: string
  positions: PositionItem[]
  loading: boolean
  error: string | null
}

export default function PositionsPanel({ symbol: selectedSymbol, positions, loading, error }: PositionsPanelProps) {
  const sortedPositions = useMemo(() => {
    const list = [...positions]
    list.sort((a, b) => {
      const symA = a.symbol ?? ''
      const symB = b.symbol ?? ''
      if (symA === selectedSymbol && symB !== selectedSymbol) return -1
      if (symA !== selectedSymbol && symB === selectedSymbol) return 1
      if (symA === selectedSymbol && symB === selectedSymbol) return 0
      return symA.localeCompare(symB, undefined, { sensitivity: 'base' })
    })
    return list
  }, [positions, selectedSymbol])

  return (
    <div className="positions-panel">
      <h3 className="positions-panel__title">Positions</h3>
      <div className="positions-panel__content">
        {loading && <span>Loading…</span>}
        {error != null && <span className="positions-panel__error">{typeof error === 'string' ? error : String(error)}</span>}
        {!loading && !error && sortedPositions.length === 0 && <span>No open position</span>}
        {!loading && sortedPositions.length > 0 && (
          <table className="positions-panel__table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Side</th>
                <th>Size</th>
                <th>Entry</th>
                <th>Mark</th>
                <th>uPnL</th>
                <th>Leverage</th>
              </tr>
            </thead>
            <tbody>
              {sortedPositions.map((p, i) => (
                <tr key={`${p.symbol}-${p.side}-${i}`}>
                  <td>
                    <Link to={`/${p.symbol}`} className="positions-panel__asset-link">
                      {p.symbol || '—'}
                    </Link>
                  </td>
                  <td>{p.side}</td>
                  <td>{p.size}</td>
                  <td>{p.entry_price}</td>
                  <td>{p.mark_price}</td>
                  <td>{p.unrealized_pnl}</td>
                  <td>{p.leverage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
