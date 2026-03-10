"""Fan-out broker: Bybit WS -> normalized events -> frontend WS clients."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.core.enums import TIMEFRAME_TO_BYBIT_INTERVAL
from app.services import bybit_ws
from app.logger import get_logger

logger = get_logger(__name__)

_loop: asyncio.AbstractEventLoop | None = None
_executor = ThreadPoolExecutor(max_workers=2)


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop

# Subscriptions we need from Bybit: set of (symbol, interval_bybit)
_active_bybit_subs: set[tuple[str, str]] = set()
# Frontend clients: list of (send_fn, set of (symbol, timeframe))
_clients: list[tuple[Any, set[tuple[str, str]]]] = []
_broker_lock = asyncio.Lock()


def _normalize_kline_msg(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Convert Bybit kline message to our candle event."""
    topic = (msg.get("topic") or "").strip()
    if not topic.startswith("kline."):
        return None
    parts = topic.split(".")
    if len(parts) != 3:
        return None
    _kline, interval, symbol = parts
    interval = str(interval)
    data_list = msg.get("data") or []
    if not data_list:
        return None
    d = data_list[0] if isinstance(data_list[0], dict) else {}
    start = d.get("start") or 0
    if isinstance(start, str):
        start = int(start)
    start_sec = start // 1000
    return {
        "type": "candle",
        "symbol": symbol,
        "timeframe": _interval_to_timeframe(interval),
        "data": {
            "time": start_sec,
            "open": str(d.get("open", "0")),
            "high": str(d.get("high", "0")),
            "low": str(d.get("low", "0")),
            "close": str(d.get("close", "0")),
            "volume": str(d.get("volume", "0")),
            "confirmed": bool(d.get("confirm", False)),
        },
    }


def _interval_to_timeframe(interval: str | int) -> str:
    """Map Bybit interval to our timeframe string."""
    interval_str = str(interval)
    rev = {v: k for k, v in TIMEFRAME_TO_BYBIT_INTERVAL.items()}
    return rev.get(interval_str, interval_str)


def _bybit_callback(msg: dict[str, Any]) -> None:
    """Called from Bybit WS thread; schedule broadcast in event loop."""
    ev = _normalize_kline_msg(msg)
    if not ev:
        return
    logger.debug("Kline received %s %s", ev.get("symbol"), ev.get("timeframe"))
    if _loop:
        try:
            _loop.call_soon_threadsafe(lambda e=ev: asyncio.create_task(_broadcast(e)))
        except Exception as ex:
            logger.warning("Failed to schedule broadcast: %s", ex)
    else:
        logger.warning("No event loop set, kline dropped for %s", ev.get("symbol"))


async def _broadcast(payload: dict[str, Any]) -> None:
    """Send payload to all clients subscribed to (symbol, timeframe)."""
    symbol = payload.get("symbol", "")
    timeframe = payload.get("timeframe", "")
    key = (symbol, timeframe)
    async with _broker_lock:
        to_send = list(_clients)
    sent = 0
    for send_fn, subs in to_send:
        if key not in subs:
            continue
        try:
            await send_fn(json.dumps(payload))
            sent += 1
        except Exception as e:
            logger.debug("Broadcast to client failed: %s", e)
    if sent:
        logger.debug("Kline broadcast %s %s to %s client(s)", symbol, timeframe, sent)


async def register_client(send_fn: Any) -> tuple[Any, set[tuple[str, str]]]:
    """Register a frontend client. Returns (send_fn, its subscription set)."""
    subs: set[tuple[str, str]] = set()
    async with _broker_lock:
        _clients.append((send_fn, subs))
    return send_fn, subs


async def unregister_client(send_fn: Any) -> None:
    async with _broker_lock:
        _clients[:] = [(s, sub) for s, sub in _clients if s != send_fn]


def _do_subscribe_kline(interval: str, symbol: str) -> None:
    """Run in thread to avoid blocking event loop."""
    bybit_ws.subscribe_kline(interval, symbol, _bybit_callback)


async def subscribe_client(send_fn: Any, subs: set[tuple[str, str]], symbol: str, timeframe: str) -> None:
    """Add (symbol, timeframe) to client's subs and ensure Bybit is subscribed."""
    symbol = symbol.upper()
    interval = TIMEFRAME_TO_BYBIT_INTERVAL.get(timeframe)
    if not interval:
        return
    subs.add((symbol, timeframe))
    key = (symbol, interval)
    if key in _active_bybit_subs:
        logger.debug("Bybit already subscribed to %s %s", symbol, timeframe)
        return
    _active_bybit_subs.add(key)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _do_subscribe_kline, interval, symbol)
    logger.info("Subscribed to Bybit kline %s %s", symbol, timeframe)


def get_status() -> dict[str, str]:
    """Connection status for status event."""
    return {
        "market_ws": "connected" if bybit_ws.is_public_connected() else "disconnected",
        "private_ws": "disconnected",
    }
