# tests/test_api.py
from datetime import datetime
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
    # Prepare a tiny fake OHLCV DataFrame (no network).
    idx = pd.to_datetime([
        "2024-01-02", "2024-01-03", "2024-01-04"
    ])
    df = pd.DataFrame(
        {
            "Open":  [100.0, 102.0, 101.5],
            "High":  [105.0, 103.0, 106.0],
            "Low":   [ 99.0, 100.0, 101.0],
            "Close": [104.0, 101.0, 105.5],
            "Volume":[1_000, 900, 1_100],
        },
        index=idx,
    )

    # Monkeypatch yfinance.download to return our fake DataFrame
    def fake_download(*args, **kwargs):
        return df

    monkeypatch.setattr(yf, "download", fake_download)

    # Exercise API (should now be deterministic and fast)
    resp = client.get("/api/stats", params={"ticker": "MSFT"})
    assert resp.status_code == 200
    body = resp.json()

    assert body["ticker"] == "MSFT"
    assert body["count"] == 3
    assert body["high"] == 106.0
    assert body["low"] == 99.0
    # Average close = (104.0 + 101.0 + 105.5) / 3 = 103.5
    assert abs(body["avg_close"] - 103.5) < 1e-9
    assert body["last_close"] == 105.5

def test_bad_upstream_returns_400(monkeypatch):
    import yfinance as yf

    def fake_download(*args, **kwargs):
        raise RuntimeError("network down")  # 一定要抛异常

    monkeypatch.setattr(yf, "download", fake_download)

    resp = client.get("/api/stats", params={"ticker": "MSFT"})
    assert resp.status_code == 400