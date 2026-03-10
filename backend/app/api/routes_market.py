"""Market data routes: historical candles."""

from fastapi import APIRouter, Query, HTTPException

from app.core.enums import TIMEFRAME_TO_BYBIT_INTERVAL
from app.schemas.market import MarketHistoryResponse, CandleItem
from app.services.bybit_rest import get_klines
from app.services.symbol_service import validate_symbol, validate_timeframe
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/history", response_model=MarketHistoryResponse)
def market_history(
    symbol: str = Query(..., description="Trading symbol e.g. XRPUSDT"),
    timeframe: str = Query("1m", description="One of: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(200, ge=1, le=1000),
) -> MarketHistoryResponse:
    """Get historical candles for symbol and timeframe."""
    norm_symbol = validate_symbol(symbol)
    try:
        tf = validate_timeframe(timeframe)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    interval = TIMEFRAME_TO_BYBIT_INTERVAL[tf]
    resp = get_klines(symbol=norm_symbol, interval=interval, limit=limit)
    result = resp.get("result") or {}
    raw_list = result.get("list") or []
    # Bybit returns [startTime, open, high, low, close, volume, turnover]
    candles: list[CandleItem] = []
    for row in reversed(raw_list):
        if isinstance(row, list) and len(row) >= 6:
            ts = int(row[0])
            if ts > 1e12:
                ts = ts // 1000
            candles.append(
                CandleItem(
                    time=ts,
                    open=str(row[1]),
                    high=str(row[2]),
                    low=str(row[3]),
                    close=str(row[4]),
                    volume=str(row[5]) if len(row) > 5 else "0",
                )
            )
        elif isinstance(row, dict):
            candles.append(
                CandleItem(
                    time=int(row.get("startTime") or row.get("start", 0)),
                    open=str(row.get("open", "0")),
                    high=str(row.get("high", "0")),
                    low=str(row.get("low", "0")),
                    close=str(row.get("close", "0")),
                    volume=str(row.get("volume", "0")),
                )
            )
    return MarketHistoryResponse(symbol=norm_symbol, timeframe=tf, candles=candles)
