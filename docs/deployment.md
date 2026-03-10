# Deployment (VPS)

## Target

- Ubuntu 22.04 or 24.04
- Docker Engine and Docker Compose plugin installed
- Firewall configured (e.g. allow 80/443)

## Steps

1. **Install Docker** (if not already):
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```
   Log out and back in so the group takes effect.

2. **Install Docker Compose plugin**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```

3. **Clone and enter project**:
   ```bash
   git clone <repo-url> bybit-terminal
   cd bybit-terminal
   ```

4. **Prepare environment**:
   ```bash
   cp .env.example .env
   # Edit .env: set BYBIT_API_KEY, BYBIT_API_SECRET (use testnet keys for safety)
   # Set BYBIT_TESTNET=true for testnet, false for mainnet
   ```

5. **Start**:
   ```bash
   docker compose up -d --build
   ```

6. **Verify**:
   - Open `http://<server-ip>/` and navigate to `http://<server-ip>/XRPUSDT`
   - Check health: `curl http://<server-ip>/api/health`
   - Check logs: `docker compose logs -f backend` and `docker compose logs -f nginx`

## Nginx behaviour

- Serves the React app at `/`; SPA routing uses `try_files ... /index.html`.
- `/api/` is proxied to the backend (FastAPI) at `http://backend:8000/api/`.
- `/ws` is proxied to the backend WebSocket at `http://backend:8000/ws` with upgrade headers.

## Optional: domain and TLS

Place a reverse proxy (e.g. Caddy or Nginx) in front with TLS, or use a load balancer with TLS termination. Point the proxy to the same Nginx container port (80) or map a different host port in `compose.yaml`.

## Commands summary

| Action   | Command |
|----------|---------|
| Start    | `docker compose up -d --build` |
| Stop     | `docker compose down` |
| Restart backend | `docker compose restart backend` |
| Logs     | `docker compose logs -f backend` or `docker compose logs -f nginx` |
| Update   | `git pull && docker compose up -d --build` |
