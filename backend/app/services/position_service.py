"""Position snapshot and normalization."""

from app.services.bybit_rest import get_positions
from app.schemas.positions import PositionsResponse, PositionItem
from app.services.symbol_service import validate_symbol
from app.logger import get_logger

logger = get_logger(__name__)


def _norm_position(p: dict) -> PositionItem | None:
    size = (p.get("size") or "0").strip()
    if not size or float(size) == 0:
        return None
    sym = (p.get("symbol") or "").strip()
    side = p.get("side") or "None"
    entry = (p.get("avgPrice") or p.get("entryPrice") or "0").strip()
    mark = (p.get("markPrice") or "0").strip()
    upnl = (p.get("unrealisedPnl") or p.get("unrealizedPnl") or "0").strip()
    lev = (p.get("leverage") or "0").strip()
    return PositionItem(
        symbol=sym,
        side=side,
        size=size,
        entry_price=entry,
        mark_price=mark,
        unrealized_pnl=upnl,
        leverage=lev,
    )


def get_positions_for_symbol(symbol: str) -> PositionsResponse:
    """Fetch positions for symbol and return normalized response."""
    norm_symbol = validate_symbol(symbol)
    resp = get_positions(symbol=norm_symbol)
    result = resp.get("result") or {}
    raw_list = result.get("list") or []
    positions: list[PositionItem] = []
    for p in raw_list:
        item = _norm_position(p)
        if item:
            if not item.symbol:
                item = PositionItem(symbol=norm_symbol, side=item.side, size=item.size, entry_price=item.entry_price, mark_price=item.mark_price, unrealized_pnl=item.unrealized_pnl, leverage=item.leverage)
            positions.append(item)
    return PositionsResponse(symbol=norm_symbol, positions=positions)


def get_all_positions() -> PositionsResponse:
    """Fetch all linear positions (each item includes symbol)."""
    resp = get_positions(symbol=None)
    result = resp.get("result") or {}
    raw_list = result.get("list") or []
    positions: list[PositionItem] = []
    for p in raw_list:
        item = _norm_position(p)
        if item:
            positions.append(item)
    return PositionsResponse(symbol="", positions=positions)
