# tests/test_api.py
import pandas as pd
import yfinance as yf
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_stats_msft_smoke(monkeypatch):
    """
    Smoke test: /api/stats should return correct statistics when
    yfinance returns a small, well-formed OHLCV DataFrame.

    We mock yfinance.Ticker().history() so the test is fast
    and does not depend on external network calls.
    """
    idx = pd.to_datetime(
        ["2024-01-02", "2024-01-03", "2024-01-04"]
    )
    df = pd.DataFrame(
        {
            "Open": [100.0, 102.0, 101.5],
            "High": [105.0, 103.0, 106.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [104.0, 101.0, 105.5],
            "Volume": [1_000, 900, 1_100],
        },
        index=idx,
    )

    class DummyTicker:
        def __init__(self, symbol: str):
            self.symbol = symbol

        def history(self, start=None, end=None):
            # ignore start/end in this mock and just return our fake df
            return df

    # Mock yfinance.Ticker to return our dummy ticker
    monkeypatch.setattr(yf, "Ticker", lambda symbol: DummyTicker(symbol))

    resp = client.get(
        "/api/stats",
        params={"ticker": "MSFT", "start": "2024-01-01", "end": "2024-12-31"},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["ticker"] == "MSFT"
    assert body["count"] == 3
    assert body["high"] == 106.0
    assert body["low"] == 99.0
    # (104 + 101 + 105.5) / 3 = 103.5
    assert abs(body["avg_close"] - 103.5) < 1e-9
    assert body["last_close"] == 105.5


def test_bad_upstream_returns_400(monkeypatch):
    """
    If yfinance raises an exception (e.g. network down), the API
    should respond with HTTP 400 instead of 500.
    """

    class BrokenTicker:
        def __init__(self, symbol: str):
            self.symbol = symbol

        def history(self, start=None, end=None):
            raise RuntimeError("network down")

    monkeypatch.setattr(yf, "Ticker", lambda symbol: BrokenTicker(symbol))

    resp = client.get(
        "/api/stats",
        params={"ticker": "MSFT", "start": "2024-01-01", "end": "2024-12-31"},
    )
    assert resp.status_code == 400
