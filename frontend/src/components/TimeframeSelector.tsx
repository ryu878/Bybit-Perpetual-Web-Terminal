const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d'] as const

interface TimeframeSelectorProps {
  value: string
  onChange: (tf: string) => void
}

export default function TimeframeSelector({ value, onChange }: TimeframeSelectorProps) {
  return (
    <div className="timeframe-selector">
      {TIMEFRAMES.map((tf) => (
        <button
          key={tf}
          type="button"
          className={`timeframe-selector__btn ${value === tf ? 'timeframe-selector__btn--active' : ''}`}
          onClick={() => onChange(tf)}
        >
          {tf}
        </button>
      ))}
    </div>
  )
}
