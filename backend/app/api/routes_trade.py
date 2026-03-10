"""Trade route: place market order, close by side, close all positions."""

from fastapi import APIRouter, Body

from app.schemas.trade import OrderRequest, OrderResponse, CloseAllRequest, CloseAllResponse, CloseRequest
from app.services.order_service import place_market_order_validated, close_position_validated
from app.services.bybit_rest import close_all_positions
from app.services.symbol_service import validate_symbol
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/trade", tags=["trade"])


@router.post("/order", response_model=OrderResponse)
def place_order(body: OrderRequest) -> OrderResponse:
    """Place market order (Buy or Sell)."""
    return place_market_order_validated(
        symbol=body.symbol,
        side=body.side,
        qty=body.qty,
    )


@router.post("/close", response_model=OrderResponse)
def close_position(body: CloseRequest) -> OrderResponse:
    """Close part of a position: side (Buy=long, Sell=short) by qty."""
    return close_position_validated(symbol=body.symbol, side=body.side, qty=body.qty)


@router.post("/close-all", response_model=CloseAllResponse)
def close_all(body: CloseAllRequest = Body(default=CloseAllRequest())) -> CloseAllResponse:
    """Close all open positions. Optional body.symbol to close only that symbol."""
    symbol = None
    if body.symbol:
        symbol = validate_symbol(body.symbol)
    closed = close_all_positions(symbol=symbol)
    return CloseAllResponse(closed=len(closed), positions=closed)
