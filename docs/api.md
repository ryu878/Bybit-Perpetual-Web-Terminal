# API Reference

## REST

Base path: `/api` (proxied by Nginx to backend).

### GET /api/health

**Response:** `200`

```json
{ "status": "ok" }
```

### GET /api/market/history

**Query:** `symbol` (required), `timeframe` (default `1m`), `limit` (default 200, max 1000).

**Response:** `200`

```json
{
  "symbol": "XRPUSDT",
  "timeframe": "1m",
  "candles": [
    {
      "time": 1710000000,
      "open": "0.6123",
      "high": "0.6150",
      "low": "0.6101",
      "close": "0.6148",
      "volume": "123456"
    }
  ]
}
```

**Errors:** `404` symbol not found or not linear perpetual; `422` invalid timeframe.

### GET /api/positions

**Query:** `symbol` (optional). If provided, returns positions for that symbol only. If omitted, returns all linear positions (each item includes `symbol`).

**Response:** `200`

```json
{
  "symbol": "XRPUSDT",
  "positions": [
    {
      "symbol": "XRPUSDT",
      "side": "Buy",
      "size": "100",
      "entry_price": "0.6100",
      "mark_price": "0.6148",
      "unrealized_pnl": "4.8",
      "leverage": "5"
    }
  ]
}
```

When `symbol` is omitted, response `symbol` is `""`. **Errors:** `404` invalid symbol (when provided); `502` exchange error.

### POST /api/trade/order

**Body:**

```json
{
  "symbol": "XRPUSDT",
  "side": "Buy",
  "qty": "100"
}
```

**Response:** `200`

```json
{
  "status": "accepted",
  "symbol": "XRPUSDT",
  "side": "Buy",
  "qty": "100",
  "exchange_order_id": "..."
}
```

**Errors:** `422` validation (side, qty); `404` symbol; `502` exchange error.

### POST /api/trade/close

Close part of a position by side (Buy = long, Sell = short) and quantity.

**Body:**

```json
{
  "symbol": "XRPUSDT",
  "side": "Buy",
  "qty": "10"
}
```

Closes 10 from the long position (Buy side). Use `"side": "Sell"` to close from the short position. Uses the same lot-size validation as place order.

**Response:** `200` (same shape as POST /api/trade/order).

**Errors:** `422` validation; `404` symbol; `502` exchange error.

### POST /api/trade/close-all

Closes all open linear positions. Optionally restrict to one symbol.

**Body (optional):**

```json
{
  "symbol": "XRPUSDT"
}
```

Omit `symbol` or send `{}` to close all linear positions.

**Response:** `200`

```json
{
  "closed": 2,
  "positions": [
    { "symbol": "XRPUSDT", "side": "Buy", "size": "100" },
    { "symbol": "BTCUSDT", "side": "Sell", "size": "0.01" }
  ]
}
```

**Errors:** `404` invalid symbol (if provided); `502` exchange error.

---

## WebSocket

**Endpoint:** `/ws` (proxied by Nginx to backend).

### Client → Server: subscribe

```json
{
  "action": "subscribe",
  "symbol": "XRPUSDT",
  "timeframe": "1m"
}
```

Supported timeframes: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`.

### Server → Client: candle

```json
{
  "type": "candle",
  "symbol": "XRPUSDT",
  "timeframe": "1m",
  "data": {
    "time": 1710000000,
    "open": "0.6123",
    "high": "0.6150",
    "low": "0.6101",
    "close": "0.6148",
    "volume": "123456",
    "confirmed": false
  }
}
```

`confirmed: true` when the candle has closed.

### Server → Client: status

```json
{
  "type": "status",
  "data": {
    "market_ws": "connected",
    "private_ws": "disconnected"
  }
}
```
