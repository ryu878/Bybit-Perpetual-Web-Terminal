"""Symbol normalization and validation (linear perpetual only)."""

from app.core.enums import SUPPORTED_TIMEFRAMES
from app.core.exceptions import SymbolNotFoundError
from app.services.bybit_rest import get_instruments_info
from app.logger import get_logger

logger = get_logger(__name__)


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase."""
    return (symbol or "").strip().upper()


def validate_symbol(symbol: str) -> str:
    """
    Validate symbol exists and is a supported linear perpetual.
    Returns normalized symbol.
    Raises SymbolNotFoundError if invalid.
    """
    norm = normalize_symbol(symbol)
    if not norm:
        raise SymbolNotFoundError("Symbol is required")
    try:
        resp = get_instruments_info(symbol=norm)
    except Exception as e:
        logger.warning("Instrument lookup failed for %s: %s", norm, e)
        raise SymbolNotFoundError(f"Could not verify symbol {norm}") from e
    result = resp.get("result")
    if not result:
        raise SymbolNotFoundError(f"Symbol {norm} not found")
    instruments = result.get("list") or []
    for inst in instruments:
        if inst.get("symbol") == norm:
            category = (inst.get("contractType") or "").lower()
            # linear perpetual: contractType "LinearPerpetual" or category linear
            if inst.get("contractType") == "LinearPerpetual" or (inst.get("category") or "").lower() == "linear":
                return norm
            raise SymbolNotFoundError(f"Symbol {norm} is not a linear perpetual contract")
    raise SymbolNotFoundError(f"Symbol {norm} not found")


def validate_timeframe(tf: str) -> str:
    """Validate timeframe is supported. Returns lowercase timeframe."""
    t = (tf or "").strip().lower()
    if t not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"Unsupported timeframe: {tf}. Supported: {SUPPORTED_TIMEFRAMES}")
    return t
