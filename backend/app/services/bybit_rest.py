"""Bybit REST API wrapper using pybit unified_trading.HTTP."""

from typing import Any

from pybit.unified_trading import HTTP

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

CATEGORY = "linear"


def _client() -> HTTP:
    return HTTP(
        testnet=settings.bybit_testnet,
        api_key=settings.bybit_api_key or None,
        api_secret=settings.bybit_api_secret or None,
    )


def get_instruments_info(symbol: str | None = None) -> dict[str, Any]:
    """Get instrument metadata. If symbol is None, returns all linear instruments (paginated)."""
    session = _client()
    kwargs: dict[str, Any] = {"category": CATEGORY}
    if symbol:
        kwargs["symbol"] = symbol
    try:
        return session.get_instruments_info(**kwargs)
    except Exception as e:
        logger.exception("get_instruments_info failed: %s", e)
        raise


def get_klines(symbol: str, interval: str, limit: int = 200, start: int | None = None, end: int | None = None) -> dict[str, Any]:
    """Get historical klines. interval: Bybit format (1, 5, 15, 60, 240, D)."""
    session = _client()
    kwargs: dict[str, Any] = {
        "category": CATEGORY,
        "symbol": symbol,
        "interval": interval,
        "limit": min(limit, 1000),
    }
    if start is not None:
        kwargs["start"] = start
    if end is not None:
        kwargs["end"] = end
    try:
        return session.get_kline(**kwargs)
    except Exception as e:
        logger.exception("get_kline failed: %s", e)
        raise


def get_wallet_balance(account_type: str = "UNIFIED", coin: str | None = None) -> dict[str, Any]:
    """Get wallet balance. accountType UNIFIED; optional coin e.g. USDT."""
    session = _client()
    kwargs: dict[str, Any] = {"accountType": account_type}
    if coin:
        kwargs["coin"] = coin
    try:
        return session.get_wallet_balance(**kwargs)
    except Exception as e:
        logger.exception("get_wallet_balance failed: %s", e)
        raise


def get_positions(symbol: str | None = None, settle_coin: str = "USDT") -> dict[str, Any]:
    """Get positions. If symbol is set, returns positions for that symbol; else all linear positions (requires settleCoin, e.g. USDT)."""
    session = _client()
    kwargs: dict[str, Any] = {"category": CATEGORY}
    if symbol:
        kwargs["symbol"] = symbol
    else:
        kwargs["settleCoin"] = settle_coin
    try:
        return session.get_positions(**kwargs)
    except Exception as e:
        logger.exception("get_positions failed: %s", e)
        raise


def _position_idx_for_order(symbol: str, side: str) -> int:
    """
    Return positionIdx for place_order: 0 (one-way), 1 (hedge Buy), 2 (hedge Sell).
    Uses BYBIT_POSITION_MODE if set; otherwise infers from existing positions.
    """
    mode = (settings.bybit_position_mode or "").strip().lower()
    if mode == "hedge":
        return 1 if side == "Buy" else 2
    if mode == "one_way" or mode == "oneway":
        return 0
    # Infer from positions: if any position has positionIdx 1 or 2, account is in hedge mode
    try:
        resp = get_positions(symbol=symbol)
        for p in (resp.get("result") or {}).get("list") or []:
            idx = p.get("positionIdx")
            if idx in (1, 2):
                return 1 if side == "Buy" else 2
    except Exception as e:
        logger.warning("Could not infer position mode for %s: %s; using one-way (0)", symbol, e)
    return 0


def place_market_order(symbol: str, side: str, qty: str) -> dict[str, Any]:
    """Place market order. side: Buy | Sell, qty: string quantity."""
    session = _client()
    position_idx = _position_idx_for_order(symbol, side)
    try:
        return session.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=qty,
            positionIdx=position_idx,
        )
    except Exception as e:
        logger.exception("place_order failed: %s", e)
        raise


def place_market_order_reduce_only(symbol: str, side: str, qty: str, position_idx: int | None = None) -> dict[str, Any]:
    """Place reduce-only market order (to close position). side: Buy | Sell, qty: string. position_idx from position if known."""
    session = _client()
    if position_idx is None:
        position_idx = _position_idx_for_order(symbol, side)
    try:
        return session.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=qty,
            reduceOnly=True,
            positionIdx=position_idx,
        )
    except Exception as e:
        logger.exception("place_order reduceOnly failed: %s", e)
        raise


def close_position_by_side(symbol: str, side: str, qty: str) -> dict[str, Any]:
    """Close part of a position by side. side: Buy (close long) or Sell (close short)."""
    close_side = "Sell" if side == "Buy" else "Buy"
    position_idx = _position_idx_for_order(symbol, side)
    return place_market_order_reduce_only(symbol, close_side, qty, position_idx=position_idx)


def close_all_positions(symbol: str | None = None) -> list[dict[str, Any]]:
    """
    Close all open positions. If symbol is set, only that symbol; otherwise all linear positions.
    Returns list of close results (one per closed position).
    """
    resp = get_positions(symbol=symbol)
    result = resp.get("result") or {}
    raw_list = result.get("list") or []
    closed: list[dict[str, Any]] = []
    for p in raw_list:
        size_str = (p.get("size") or "0").strip()
        if not size_str or float(size_str) == 0:
            continue
        sym = (p.get("symbol") or "").strip()
        side = (p.get("side") or "None").strip()
        if not sym or side not in ("Buy", "Sell"):
            continue
        position_idx = p.get("positionIdx", 0)
        if position_idx not in (0, 1, 2):
            position_idx = 1 if side == "Buy" else 2
        close_side = "Sell" if side == "Buy" else "Buy"
        try:
            place_market_order_reduce_only(sym, close_side, size_str, position_idx=position_idx)
            closed.append({"symbol": sym, "side": side, "size": size_str})
        except Exception as e:
            logger.exception("close_all_positions: failed to close %s %s: %s", sym, side, e)
            raise
    return closed
