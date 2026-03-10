"""Position schemas."""

from pydantic import BaseModel, Field


class PositionItem(BaseModel):
    symbol: str = ""  # Asset/symbol (e.g. XRPUSDT)
    side: str  # "Buy" | "Sell"
    size: str
    entry_price: str
    mark_price: str
    unrealized_pnl: str
    leverage: str = "0"


class PositionsResponse(BaseModel):
    symbol: str  # Requested symbol or "" when all
    positions: list[PositionItem] = Field(default_factory=list)
