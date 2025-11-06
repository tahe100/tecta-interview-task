# app/main.py
# FastAPI entrypoint. Provides /api/health and /api/stats.
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional

from .models import StatsResponse
from .services import compute_stats

app = FastAPI(
    title="Tecta Stock Stats API",
    version="1.0.0",
    description="Fetches historical prices via yfinance and returns basic statistics.",
)


@app.get("/api/health")
def health():
    # Simple liveness endpoint
    return {"status": "ok"}


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(
    ticker: str = Query(..., min_length=1, description="Ticker symbol, e.g. MSFT"),
    start: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
):
    """
    Returns basic statistics for the given ticker and optional date range.
    If no dates are provided, defaults to the last 1y of data (handled in service).
    """
    try:
        stats = compute_stats(ticker=ticker.strip().upper(), start=start, end=end)
        if stats is None:
            raise HTTPException(status_code=404, detail="No data found for given range.")
        return JSONResponse(content=stats.dict())
    except ValueError as e:
        # Service raises ValueError for user-facing errors (e.g., invalid dates)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Safety net for unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
