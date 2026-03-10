# Design Decisions

- **Backend mediates exchange access**: Keeps API keys server-side, simplifies frontend, and allows normalization and rate limiting in one place.

- **pybit**: Official Bybit SDK; supports unified trading (REST + WebSocket) and is maintained.

- **FastAPI**: Async support, automatic OpenAPI, type hints, and good performance for REST and WebSocket.

- **React + Vite**: Fast dev experience and production builds; TypeScript for type safety.

- **Nginx**: Single entrypoint to serve the SPA and proxy `/api` and `/ws` to the backend; no CORS or direct backend exposure needed.

- **Redis optional**: v1 runs a single backend instance with in-memory cache and stream broker. Redis would be added only for multi-instance or shared pub/sub.

- **Poetry**: Reliable dependency and lockfile management for Python; recommended for applications.
