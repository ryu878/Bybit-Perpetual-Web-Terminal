"""WebSocket endpoint: frontend connects here, backend bridges Bybit streams."""

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services import stream_broker
from app.services.symbol_service import validate_symbol, validate_timeframe
from app.core.enums import SUPPORTED_TIMEFRAMES
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["ws"])


async def _send(ws: WebSocket, data: str) -> None:
    await ws.send_text(data)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    send_fn = lambda data: _send(ws, data)
    _, subs = await stream_broker.register_client(send_fn)
    try:
        # Send initial status
        await send_fn(
            json.dumps(
                {
                    "type": "status",
                    "data": stream_broker.get_status(),
                }
            )
        )
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            action = (msg.get("action") or "").strip().lower()
            if action == "subscribe":
                symbol = (msg.get("symbol") or "").strip().upper()
                timeframe = (msg.get("timeframe") or "1m").strip().lower()
                if not symbol or timeframe not in SUPPORTED_TIMEFRAMES:
                    continue
                try:
                    validate_symbol(symbol)
                    validate_timeframe(timeframe)
                except Exception:
                    continue
                await stream_broker.subscribe_client(send_fn, subs, symbol, timeframe)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.debug("WebSocket error: %s", e)
    finally:
        await stream_broker.unregister_client(send_fn)
