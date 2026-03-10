"""Trade/order route validation."""

import pytest


def test_place_order_validation_side(client):
    resp = client.post(
        "/api/trade/order",
        json={"symbol": "XRPUSDT", "side": "Invalid", "qty": "100"},
    )
    # 422 validation (Pydantic) or our ValidationError
    assert resp.status_code in (422, 400)


def test_place_order_validation_qty(client):
    resp = client.post(
        "/api/trade/order",
        json={"symbol": "XRPUSDT", "side": "Buy", "qty": "-1"},
    )
    assert resp.status_code in (422, 400, 502)
