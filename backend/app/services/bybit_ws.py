"""Bybit WebSocket wrapper: public kline and ticker, optional private position stream.

Match the approach from working pybit usage: create WebSocket with only testnet and
channel_type (no global callback). Then register per-stream callbacks via kline_stream()
so pybit's default _handle_incoming_message dispatches messages to our callback.
"""

import threading
from typing import Any, Callable

from pybit.unified_trading import WebSocket

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

# Bybit WS kline interval: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M
_public_ws: WebSocket | None = None
_public_ws_lock = threading.Lock()


def _get_public_ws() -> WebSocket:
    """Get or create public WebSocket (linear channel). Do not pass callback_function
    so pybit uses its default dispatcher and invokes our per-topic callbacks."""
    global _public_ws
    with _public_ws_lock:
        if _public_ws is None:
            _public_ws = WebSocket(
                channel_type="linear",
                testnet=settings.bybit_testnet,
            )
            logger.info("Bybit public WebSocket (linear) created")
        return _public_ws


def subscribe_kline(interval: str, symbol: str, callback: Callable[[dict[str, Any]], None]) -> None:
    """Subscribe to kline stream. interval: 1, 5, 15, 60, 240, D."""
    ws = _get_public_ws()
    # Bybit WS expects interval as int for minutes (1,5,15,30,60,120,240,360,720); string for D,W,M
    interval_arg: int | str
    if interval in ("D", "W", "M"):
        interval_arg = interval
    else:
        try:
            interval_arg = int(interval)
        except (TypeError, ValueError):
            interval_arg = interval
    ws.kline_stream(interval_arg, [symbol], callback)
    logger.info("Subscribed to kline %s %s", interval_arg, symbol)


def subscribe_ticker(symbol: str, callback: Callable[[dict[str, Any]], None]) -> None:
    """Subscribe to ticker stream."""
    ws = _get_public_ws()
    ws.ticker_stream([symbol], callback)
    logger.info("Subscribed to ticker %s", symbol)


def is_public_connected() -> bool:
    try:
        return _public_ws is not None and _public_ws.is_connected()
    except Exception:
        return False
