# app/services.py
# Business logic layer: fetch historical prices from yfinance, compute statistics,
# apply default date ranges, and optionally return cached results.

from __future__ import annotations
import pandas as pd
import yfinance as yf
from datetime import date, timedelta
from typing import Optional

from .models import StatsResponse
from .cache import get as cache_get, set_ as cache_set, make_key


def _normalize_range(start: Optional[date], end: Optional[date]) -> tuple[date, date]:
    """
    Normalize the date range provided by the user.

    Rules:
        - If both start and end are provided but start > end -> invalid input.
        - If end is missing -> use today's date.
        - If start is missing -> default to 365 days before the resolved end date.

    Returns:
        A tuple (start_date, end_date) guaranteed to be valid and usable for querying.
    """
    if start and end and start > end:
        raise ValueError("start must be <= end")

    if not end:
        end = date.today()
    if not start:
        start = end - timedelta(days=365)

    return start, end


def compute_stats(ticker: str, start: Optional[date], end: Optional[date]) -> Optional[StatsResponse]:
    """
    Fetch OHLCV price data for a given ticker and compute aggregate statistics.

    Workflow:
        1. Normalize the date range (apply defaults if missing).
        2. Check if the result is already in cache (based on ticker + range).
        3. If not cached, fetch historical daily price data from yfinance.
        4. Compute:
            - Highest price in the range
            - Lowest price in the range
            - Average closing price
            - Last available closing price
            - Number of returned trading days
        5. Store the computed result in cache.
        6. Return a populated StatsResponse Pydantic model.

    Args:
        ticker (str): Stock ticker symbol to query (e.g., "MSFT").
        start (Optional[date]): Optional start date from API query.
        end (Optional[date]): Optional end date from API query.

    Returns:
        StatsResponse | None:
            - StatsResponse if data was successfully retrieved and processed.
            - None if yfinance returned no data for the given range (invalid ticker or empty period).
    """
    # Normalize and validate date inputs
    start_d, end_d = _normalize_range(start, end)

    # Construct a unique cache key for this query
    key = make_key("stats", ticker, start_d.isoformat(), end_d.isoformat())

    # Return cached result if available
    cached = cache_get(key)
    if cached:
        return cached

        # app/services.py 片段
    try:
        # Fetch OHLCV data from Yahoo Finance via yfinance
        # Note: end + 1 day ensures that the end date is inclusive.
        t = yf.Ticker(ticker)
        df: pd.DataFrame = t.history(start=start_d, end=end_d + timedelta(days=1)
        )
    except Exception as e:
        # Wrap upstream errors as ValueError so the API returns 400 instead of 500.
        raise ValueError(f"Failed to fetch data for {ticker}: {e}") from e

    # No data returned (invalid ticker or empty date range)
    if df is None or df.empty:
        return None

    # Normalize column names such as "Close", "High", "Low"
    df = df.rename(columns=str.title)

    # Compute key statistics
    high = float(df["High"].max())
    low = float(df["Low"].min())
    avg_close = float(df["Close"].mean())
    last_close = float(df["Close"].iloc[-1]) if not df["Close"].empty else None

    # Build structured API response
    result = StatsResponse(
        ticker=ticker,
        start=start_d.isoformat(),
        end=end_d.isoformat(),
        count=int(len(df)),
        high=round(high, 6),
        low=round(low, 6),
        avg_close=round(avg_close, 6),
        last_close=round(last_close, 6) if last_close is not None else None,
    )

    # Cache the computed statistics for faster future responses
    cache_set(key, result)

    return result
