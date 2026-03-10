export interface CandleItem {
  time: number
  open: string
  high: string
  low: string
  close: string
  volume: string
}

export interface MarketHistoryResponse {
  symbol: string
  timeframe: string
  candles: CandleItem[]
}

export interface PositionItem {
  symbol: string
  side: string
  size: string
  entry_price: string
  mark_price: string
  unrealized_pnl: string
  leverage: string
}

export interface PositionsResponse {
  symbol: string
  positions: PositionItem[]
}

export interface OrderRequest {
  symbol: string
  side: string
  qty: string
}

export interface OrderResponse {
  status: string
  symbol: string
  side: string
  qty: string
  exchange_order_id: string
}
