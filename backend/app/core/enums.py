"""Enums for category and timeframes."""

from enum import Enum


class Category(str, Enum):
    """Bybit product category. v1 supports linear only."""
    LINEAR = "linear"


# Bybit REST kline interval: 1,3,5,15,30,60,120,240,360,720,D,M,W
# Our supported timeframes: 1m, 5m, 15m, 1h, 4h, 1d
TIMEFRAME_TO_BYBIT_INTERVAL: dict[str, str] = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D",
}

SUPPORTED_TIMEFRAMES = list(TIMEFRAME_TO_BYBIT_INTERVAL.keys())
