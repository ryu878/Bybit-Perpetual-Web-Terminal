"""In-memory cache for active market data (candles/ticker). Optional Redis later."""

from typing import Any

from app.logger import get_logger

logger = get_logger(__name__)

# In-memory: key (symbol, timeframe) -> last candles or ticker
_cache: dict[tuple[str, str], Any] = {}


def get_cached_candles(symbol: str, timeframe: str) -> list[dict[str, Any]] | None:
    key = (symbol.upper(), timeframe)
    return _cache.get(key)


def set_cached_candles(symbol: str, timeframe: str, candles: list[dict[str, Any]]) -> None:
    key = (symbol.upper(), timeframe)
    _cache[key] = candles


def get_cached_ticker(symbol: str) -> dict[str, Any] | None:
    key = (symbol.upper(), "_ticker")
    return _cache.get(key)


def set_cached_ticker(symbol: str, data: dict[str, Any]) -> None:
    key = (symbol.upper(), "_ticker")
    _cache[key] = data
