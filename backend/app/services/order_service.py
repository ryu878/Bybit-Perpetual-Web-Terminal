"""Order validation and placement (market only)."""

from decimal import Decimal
from typing import Any

from app.core.exceptions import ValidationError
from app.services.bybit_rest import get_instruments_info, place_market_order, close_position_by_side
from app.services.symbol_service import validate_symbol
from app.schemas.trade import OrderResponse
from app.logger import get_logger

logger = get_logger(__name__)


def _get_lot_size(symbol: str) -> tuple[Decimal, Decimal, Decimal]:
    """Returns (minQty, maxQty, qtyStep) from instrument info (Bybit v5)."""
    resp = get_instruments_info(symbol=symbol)
    result = resp.get("result") or {}
    for inst in result.get("list") or []:
        if inst.get("symbol") != symbol:
            continue
        lot = inst.get("lotSizeFilter")
        if isinstance(lot, dict):
            min_qty = Decimal(lot.get("minOrderQty") or "0")
            max_qty = Decimal(lot.get("maxMktOrderQty") or lot.get("maxOrderQty") or "999999999")
            step = Decimal(lot.get("qtyStep") or "0.001")
            return (min_qty, max_qty, step)
    return (Decimal("0"), Decimal("999999999"), Decimal("0.001"))


def _round_qty_to_step(qty: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return qty
    n = (qty / step).quantize(Decimal("1"))
    return (n * step).quantize(step)


def place_market_order_validated(symbol: str, side: str, qty: str) -> OrderResponse:
    """Validate side and qty, round qty to lot size, place market order."""
    norm_symbol = validate_symbol(symbol)
    side_clean = (side or "").strip()
    if side_clean not in ("Buy", "Sell"):
        raise ValidationError("side must be Buy or Sell")
    try:
        qty_dec = Decimal(str(qty).strip())
    except Exception:
        raise ValidationError("Invalid quantity")
    if qty_dec <= 0:
        raise ValidationError("Quantity must be positive")
    min_qty, max_qty, step = _get_lot_size(norm_symbol)
    if qty_dec < min_qty:
        raise ValidationError(f"Quantity below minimum {min_qty}")
    if qty_dec > max_qty:
        raise ValidationError(f"Quantity above maximum {max_qty}")
    qty_rounded = _round_qty_to_step(qty_dec, step)
    qty_str = str(qty_rounded).rstrip("0").rstrip(".")
    if "." in qty_str:
        qty_str = qty_str[: len(qty_str)]
    try:
        result: dict[str, Any] = place_market_order(norm_symbol, side_clean, qty_str)
    except Exception as e:
        logger.warning("Place order failed: %s", e)
        raise
    res_result = result.get("result") or {}
    order_id = res_result.get("orderId") or res_result.get("orderID") or ""
    return OrderResponse(
        status="accepted",
        symbol=norm_symbol,
        side=side_clean,
        qty=qty_str,
        exchange_order_id=order_id,
    )


def close_position_validated(symbol: str, side: str, qty: str) -> OrderResponse:
    """Validate symbol, side and qty, then close that side of the position by qty."""
    norm_symbol = validate_symbol(symbol)
    side_clean = (side or "").strip()
    if side_clean not in ("Buy", "Sell"):
        raise ValidationError("side must be Buy or Sell")
    try:
        qty_dec = Decimal(str(qty).strip())
    except Exception:
        raise ValidationError("Invalid quantity")
    if qty_dec <= 0:
        raise ValidationError("Quantity must be positive")
    min_qty, max_qty, step = _get_lot_size(norm_symbol)
    if qty_dec < min_qty:
        raise ValidationError(f"Quantity below minimum {min_qty}")
    if qty_dec > max_qty:
        raise ValidationError(f"Quantity above maximum {max_qty}")
    qty_rounded = _round_qty_to_step(qty_dec, step)
    qty_str = str(qty_rounded).rstrip("0").rstrip(".")
    if "." in qty_str:
        qty_str = qty_str[: len(qty_str)]
    try:
        result: dict[str, Any] = close_position_by_side(norm_symbol, side_clean, qty_str)
    except Exception as e:
        logger.warning("Close position failed: %s", e)
        raise
    res_result = result.get("result") or {}
    order_id = res_result.get("orderId") or res_result.get("orderID") or ""
    return OrderResponse(
        status="accepted",
        symbol=norm_symbol,
        side=side_clean,
        qty=qty_str,
        exchange_order_id=order_id,
    )
