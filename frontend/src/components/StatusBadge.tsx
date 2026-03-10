type WsStatus = 'connected' | 'reconnecting' | 'disconnected'

interface StatusBadgeProps {
  status: WsStatus
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const cls =
    status === 'connected'
      ? 'status-badge--connected'
      : status === 'reconnecting'
        ? 'status-badge--reconnecting'
        : 'status-badge--disconnected'
  const label = status === 'connected' ? 'connected' : status === 'reconnecting' ? 'reconnecting' : 'disconnected'
  return <span className={`status-badge ${cls}`}>{label}</span>
}
