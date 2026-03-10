# Bybit Perpetual Web Terminal

Production-oriented v1 web trading terminal for Bybit perpetual contracts only.
<img width="1295" height="1025" alt="image" src="https://github.com/user-attachments/assets/05c1c07c-fe7f-4a8c-85eb-7b02e63a0d7d" />

## Why this project exists

This project was created as a practical trading interface layer on top of Bybit perpetuals for situations where the standard exchange web interface is not convenient enough for daily operational work.

The terminal is designed to solve several real problems:

### 1. Reduce dependence on the standard Bybit web session

The regular Bybit web interface may periodically require re-login, additional confirmation, or session recovery. That is inconvenient when the terminal is used frequently during the day or when fast access to trading is important.
This project provides a dedicated lightweight interface focused only on the essential trading workflow: chart, positions, size input, Buy, and Sell.

### 2. Safely provide trading access to another person

Sometimes it is necessary to let another person trade on an account without giving full account control.
This terminal is intended for a setup where exchange access is restricted to trading only, without withdrawal permissions and without exposing the main account environment. The user works through a controlled interface with a limited set of actions, while API keys remain only on the backend.

### 3. Create a simpler and more controlled operational interface

The full exchange UI includes many sections, settings, widgets, and account features that may be unnecessary for a focused trading workflow.
This project provides a compact single-purpose terminal that reduces distractions, keeps the workflow consistent, and allows the interface to be adapted exactly to the trading process that is actually needed.

### 4. Separate trading execution from the exchange website

The project gives an independent interface layer between the trader and the exchange website.
That makes it easier to:

- keep the workflow stable

- control which actions are available

- deploy the terminal on a VPS or private server

- extend the interface later with custom logic, logging, guardrails, or strategy-specific tools

In short, this project is made for users who need a minimal, fast, controlled, and delegation-friendly trading terminal for Bybit perpetual contracts.

## Overview

- **Single-page terminal**: Symbol from URL (e.g. `/XRPUSDT`), candlestick chart, positions panel, order panel.
- **Backend**: Python 3.11+, FastAPI, Uvicorn, pybit. REST for history/positions/orders; WebSocket bridge for live data.
- **Frontend**: React, TypeScript, Vite. Connects to backend only (no direct Bybit access).
- **Infra**: Docker, Docker Compose, Nginx (static + reverse proxy). Optional Redis.

## Architecture Summary

- **Nginx**: Serves React SPA, proxies `/api` and `/ws` to backend.
- **Backend**: Validates symbol, fetches candles/positions via REST, places orders, bridges Bybit WebSocket to frontend.
- **Frontend**: Reads symbol from URL, loads history and positions, subscribes to live stream, submits orders via API.

## Local Setup

1. **Clone and enter project**
   ```bash
   cd bybit-terminal
   ```

2. **Backend (Poetry)**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env: set BYBIT_API_KEY, BYBIT_API_SECRET (testnet keys recommended)
   poetry install
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **With Docker**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   docker compose up -d --build
   ```
   Then open http://127.0.0.1/XRPUSDT (or the port Nginx exposes).

## Environment Variables

See `.env.example`. Key variables:

- `BYBIT_TESTNET`: `true` for testnet (default), `false` for mainnet.
- `BYBIT_API_KEY` / `BYBIT_API_SECRET`: Bybit API credentials (keep server-side only).
- `BYBIT_POSITION_MODE`: Optional. `one_way` or `hedge`. If your account is in **hedge mode** and you get error 10001 ("position idx not match position mode"), set `BYBIT_POSITION_MODE=hedge`. Leave empty to auto-detect from existing positions.
- `REDIS_ENABLED` / `REDIS_URL`: Optional Redis for multi-instance or pub/sub.

## Docker Usage

- **Start**: `docker compose up -d --build`
- **Stop**: `docker compose down`
- **Logs**: `docker compose logs -f backend` or `docker compose logs -f nginx`

## Build and update after code changes

From the **bybit-terminal** directory (where `compose.yaml` lives):

```bash
cd /path/to/bybit-terminal
docker compose build --no-cache
docker compose up -d
```

Or in one step:

```bash
docker compose up -d --build
```

Use `--no-cache` when you want to force a full rebuild (e.g. frontend changes not showing). After updating, do a **hard refresh** in the browser (Ctrl+Shift+R / Cmd+Shift+R) to avoid cached JS/CSS.

## Nginx Role

- Serves built React app (SPA fallback).
- Proxies `/api/` to backend FastAPI.
- Proxies `/ws` to backend WebSocket.

## Testnet Safety

The app defaults to **Bybit testnet**. Use testnet keys for development and verification. Do not put mainnet keys in `.env` unless you intend to trade real funds.

## Example URLs

- http://127.0.0.1/XRPUSDT
- http://127.0.0.1/BTCUSDT
- http://127.0.0.1/ETHUSDT

## Troubleshooting

- **Chart not loading**: Check backend logs; ensure symbol is valid perpetual (e.g. XRPUSDT).
- **WebSocket disconnect**: Backend reconnects to Bybit automatically; frontend reconnects to backend. Check nginx proxy and backend logs.
- **Charts not updating live**: Ensure backend is receiving Bybit kline stream. Run with `APP_ENV=development` (or set log level to DEBUG) and check backend logs for "Subscribed to Bybit kline" and "Kline received" / "Kline broadcast". If you see subscribe but no kline logs, the Bybit WebSocket may not be pushing (check testnet/mainnet and symbol).
- **Orders failing**: Verify API key has trading permissions and testnet/mainnet matches `.env`.
- **Positions / "Unmatched IP"**: Your Bybit API key has IP whitelist enabled. Add your server’s (or machine’s) public IP in Bybit API Management, or create a key without IP restriction for development.

## Running tests

Backend (from `backend/` with Poetry and Python 3.11+):

```bash
cd backend
poetry install
poetry run pytest tests/ -v
```

## Test checklist (manual)

- Open `/XRPUSDT` and confirm XRPUSDT terminal loads.
- Switch timeframes (1m, 5m, 15m, 1h, 4h, 1d) and confirm chart reloads.
- Confirm chart loads initial candles from REST.
- Confirm live candle updates (WebSocket) after a short delay.
- Confirm positions panel shows "No open position" or current position.
- Enter quantity and place Buy/Sell (testnet); confirm success or error message.
- Confirm Nginx: `/api/health` returns `{"status":"ok"}`, `/ws` upgrades to WebSocket.

See `docs/` for architecture, API, deployment, operations, and decisions.

## Project tree

```
bybit-terminal/
├── README.md
├── .env.example
├── .gitignore
├── compose.yaml
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   ├── operations.md
│   └── decisions.md
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── nginx.conf
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router/
│       ├── pages/
│       ├── components/
│       ├── hooks/
│       ├── api/
│       ├── types/
│       └── styles/
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── core/
│   └── tests/
└── infra/
    └── nginx/
```

## Design summary

- **Backend mediates Bybit**: All exchange access (REST + WebSocket) goes through the backend; API keys stay server-side.
- **Single backend, in-memory broker**: No Redis in v1; stream broker and cache are in-process.
- **REST for snapshots and orders**: History, positions, and order placement use pybit HTTP.
- **WebSocket for live candles**: Backend subscribes to Bybit kline stream and fans out normalized events to frontend clients.
- **SPA + Nginx**: React app served by Nginx with `try_files` for routing; `/api` and `/ws` proxied to backend.


***
## About
## 📌 Quantitative Researcher | Algorithmic Trader | Trading Systems Architect

Quantitative researcher and trading systems engineer with end-to-end ownership of systematic strategies — from research and statistical validation to execution architecture and 24/7 production deployment.

Experience across crypto (CEX/DEX), FX, and exchange-traded markets.

Core focus areas:
- Systematic strategy design, validation, and robustness testing
- Market microstructure analysis (order book dynamics, liquidity, spread behavior, funding, volume delta)
- Tick-level and historical backtesting framework development
- Execution engine architecture and order lifecycle management
- Real-time market data processing pipelines
- Risk-aware system design and capital efficiency
- Production-grade trading infrastructure

## Technical Stack

- **Languages:** Python, C++, MQL5
- **Execution & Connectivity:** REST, WebSocket, FIX
- **Infrastructure:** Linux, Docker, Redis, PostgreSQL, ClickHouse
- **Analytics:** NumPy, Pandas, custom backtesting frameworks

## Contact

**Email:** ryu8777@gmail.com
***
