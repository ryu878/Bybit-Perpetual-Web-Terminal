"""Positions endpoint (may 404/502 if symbol invalid or API unreachable)."""

def test_positions_accepts_symbol(client):
    resp = client.get("/api/positions", params={"symbol": "XRPUSDT"})
    # 200 with positions list, or 404/502 from backend/Bybit
    assert resp.status_code in (200, 404, 502)
    if resp.status_code == 200:
        data = resp.json()
        assert "symbol" in data
        assert "positions" in data
