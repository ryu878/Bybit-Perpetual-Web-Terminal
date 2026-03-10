# Architecture

## Overview

The Bybit Perpetual Web Terminal is a single-page web app with a backend that mediates all exchange access. The frontend never talks to Bybit directly.

## Components

### Frontend (React + Vite + TypeScript)

- **Responsibility**: UI only. Reads symbol from URL (`/:symbol`), displays chart, positions, and order panel. Sends all API and WebSocket traffic to the backend.
- **Data flow**: REST for initial history and positions; WebSocket for live candles and (optional) position updates. Order placement via REST POST.

### Backend (FastAPI + Python)

- **Responsibility**: Validate symbol and timeframe, call Bybit REST/WebSocket, normalize responses, and expose a simple REST + WebSocket API to the frontend. Keeps API key/secret server-side.
- **Data flow**: Incoming REST → pybit HTTP → Bybit; incoming WebSocket subscribe → Bybit public WS (kline) → normalize → fan-out to frontend clients.

### Nginx

- **Responsibility**: Serve the built React app (SPA), proxy `/api/` to the backend, proxy `/ws` to the backend WebSocket. Handles SPA fallback and optional gzip/cache headers.

## REST vs WebSocket

- **REST**: Health, market history (candles), positions snapshot, place order. Used for one-off or initial loads.
- **WebSocket**: Live kline updates for the active symbol/timeframe. Frontend connects to `/ws`, sends `subscribe` with symbol and timeframe; backend subscribes to Bybit kline stream and forwards normalized candle events.

## Optional Redis

Redis is not required for v1. The backend uses in-memory state for the stream broker and market cache. Redis would be added only if we need pub/sub across multiple backend workers or a shared cache across instances.
