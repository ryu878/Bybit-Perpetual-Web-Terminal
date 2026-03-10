"""Symbol normalization and validation."""

import pytest
from app.services.symbol_service import normalize_symbol, validate_timeframe
from app.core.enums import SUPPORTED_TIMEFRAMES


def test_normalize_symbol():
    assert normalize_symbol("xrpusdt") == "XRPUSDT"
    assert normalize_symbol("  btcusdt  ") == "BTCUSDT"
    assert normalize_symbol("ETHUSDT") == "ETHUSDT"


def test_validate_timeframe():
    for tf in SUPPORTED_TIMEFRAMES:
        assert validate_timeframe(tf) == tf
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        validate_timeframe("2h")
    with pytest.raises(ValueError, match="Unsupported"):
        validate_timeframe("")
