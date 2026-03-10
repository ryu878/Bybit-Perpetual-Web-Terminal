"""Positions snapshot route."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.positions import PositionsResponse
from app.services.position_service import get_positions_for_symbol, get_all_positions
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("", response_model=PositionsResponse)
def get_positions(
    symbol: Annotated[str | None, Query(description="Trading symbol e.g. XRPUSDT; omit to return all positions")] = None,
) -> PositionsResponse:
    """Get positions for symbol, or all linear positions when symbol is omitted."""
    if symbol and symbol.strip():
        return get_positions_for_symbol(symbol.strip())
    return get_all_positions()
