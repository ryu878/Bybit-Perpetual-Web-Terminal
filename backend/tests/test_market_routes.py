"""Market history endpoint (mocked)."""

from unittest.mock import patch


@patch("app.api.routes_market.validate_symbol", return_value="XRPUSDT")
@patch("app.api.routes_market.get_klines")
def test_market_history_returns_200_and_structure(mock_get_klines, _mock_validate, client):
    mock_get_klines.return_value = {
        "result": {
            "list": [
                [1710000000000, "0.61", "0.62", "0.60", "0.615", "123456"],
            ]
        }
    }
    resp = client.get("/api/market/history", params={"symbol": "XRPUSDT", "timeframe": "1m"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "XRPUSDT"
    assert data["timeframe"] == "1m"
    assert "candles" in data
    assert isinstance(data["candles"], list)


def test_market_history_invalid_timeframe(client):
    resp = client.get(
        "/api/market/history",
        params={"symbol": "XRPUSDT", "timeframe": "2h"},
    )
    assert resp.status_code == 422
