# Operations

## Logs

- **Backend**: `docker compose logs -f backend`
- **Nginx**: `docker compose logs -f nginx`

Logs include REST failures, WebSocket reconnects, subscription changes, and order submission results.

## Restart

- Restart backend only: `docker compose restart backend`
- Restart all: `docker compose down && docker compose up -d`

## Rebuild / update

```bash
git pull
docker compose up -d --build
```

## Common issues

1. **Chart not loading / 404 on history**
   - Ensure symbol is a valid linear perpetual (e.g. XRPUSDT, BTCUSDT). Check backend logs for "Symbol ... not found".

2. **WebSocket disconnects**
   - Backend reconnects to Bybit automatically. Frontend reconnects to backend after a few seconds. Check Nginx proxy and backend logs for errors.

3. **Orders failing**
   - Verify API key has trading permissions. Ensure BYBIT_TESTNET in `.env` matches the key type (testnet vs mainnet).

4. **502 Bad Gateway**
   - Backend may be down or not ready. Run `docker compose ps` and `docker compose logs backend`.

## Recovering from WebSocket disconnects

No manual action required. The backend and frontend both implement reconnect logic. If problems persist, restart the backend: `docker compose restart backend`.
