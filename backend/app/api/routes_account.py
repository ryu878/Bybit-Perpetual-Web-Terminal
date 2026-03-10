"""Account wallet/margin balance."""

from fastapi import APIRouter

from app.services.bybit_rest import get_wallet_balance
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/wallet-balance")
def wallet_balance() -> dict[str, str]:
    """
    Return margin summary for display: initial_margin_pct, maintenance_margin_pct,
    margin_balance, available_balance (all strings; rates as "0.00" percent).
    """
    resp = get_wallet_balance(account_type="UNIFIED", coin="USDT")
    result = resp.get("result") or {}
    rows = result.get("list") or []
    default = {
        "initial_margin_pct": "0.00",
        "maintenance_margin_pct": "0.00",
        "margin_balance": "0",
        "available_balance": "0",
    }
    if not rows:
        return default
    acc = rows[0]
    try:
        im_rate = float(acc.get("accountIMRate") or 0)
        mm_rate = float(acc.get("accountMMRate") or 0)
        total_margin = (acc.get("totalMarginBalance") or "0").strip()
        total_avail = (acc.get("totalAvailableBalance") or "0").strip()
        return {
            "initial_margin_pct": f"{im_rate * 100:.2f}",
            "maintenance_margin_pct": f"{mm_rate * 100:.2f}",
            "margin_balance": total_margin,
            "available_balance": total_avail,
        }
    except (TypeError, ValueError) as e:
        logger.warning("wallet_balance parse: %s", e)
        return default
