"""Market/candle schemas."""

from pydantic import BaseModel, Field


class CandleItem(BaseModel):
    time: int
    open: str
    high: str
    low: str
    close: str
    volume: str


class MarketHistoryResponse(BaseModel):
    symbol: str
    timeframe: str
    candles: list[CandleItem] = Field(default_factory=list)
