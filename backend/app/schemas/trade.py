"""Trade/order schemas."""

from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    symbol: str
    side: str  # "Buy" | "Sell"
    qty: str


class OrderResponse(BaseModel):
    status: str = "accepted"
    symbol: str
    side: str
    qty: str
    exchange_order_id: str = ""


class CloseAllRequest(BaseModel):
    """Optional symbol to close only that symbol; omit to close all linear positions."""

    symbol: str | None = None


class CloseAllResponse(BaseModel):
    closed: int
    positions: list[dict[str, str]] = []  # [{ "symbol", "side", "size" }, ...]


class CloseRequest(BaseModel):
    """Close part of a position: side (Buy=long, Sell=short) and qty to close."""

    symbol: str
    side: str  # "Buy" | "Sell"
    qty: str
