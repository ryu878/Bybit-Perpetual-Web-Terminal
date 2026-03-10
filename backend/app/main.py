"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes_health import router as health_router
from app.api.routes_market import router as market_router
from app.api.routes_positions import router as positions_router
from app.api.routes_trade import router as trade_router
from app.api.routes_account import router as account_router
from app.api.routes_ws import router as ws_router
from app.config import settings
from app.core.exceptions import SymbolNotFoundError, ValidationError, ExchangeError
from app.logger import setup_logging

try:
    from pybit.exceptions import (
        FailedRequestError,
        InvalidRequestError,
        UnauthorizedExceptionError,
    )
    PYBIT_EXCEPTIONS = (InvalidRequestError, FailedRequestError, UnauthorizedExceptionError)
except ImportError:
    PYBIT_EXCEPTIONS = ()

setup_logging("INFO" if settings.app_env == "production" else "DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from app.services import stream_broker
    stream_broker.set_event_loop(asyncio.get_running_loop())
    yield
    # Shutdown: close Bybit WS, etc. (optional)


app = FastAPI(
    title="Bybit Terminal API",
    lifespan=lifespan,
)


def _err(message: str, status: int = 400) -> JSONResponse:
    return JSONResponse(content={"detail": message}, status_code=status)


@app.exception_handler(SymbolNotFoundError)
def handle_symbol_not_found(_, exc: SymbolNotFoundError):
    return _err(str(exc), 404)


@app.exception_handler(ValidationError)
def handle_validation(_, exc: ValidationError):
    return _err(str(exc), 422)


@app.exception_handler(ExchangeError)
def handle_exchange(_, exc: ExchangeError):
    return _err(str(exc), 502)


def _handle_pybit(_, exc: Exception):
    return _err(str(exc), 502)


for _exc_cls in PYBIT_EXCEPTIONS:
    app.exception_handler(_exc_cls)(_handle_pybit)


app.include_router(health_router, prefix="/api")
app.include_router(market_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(trade_router, prefix="/api")
app.include_router(account_router, prefix="/api")
app.include_router(ws_router)
