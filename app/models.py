# app/models.py
# Pydantic schemas for structured API responses.

from pydantic import BaseModel
from typing import Optional


class StatsResponse(BaseModel):
    """
    Response model returned by the /api/stats endpoint.
    It provides basic statistical information over a selected time range
    for a given stock ticker.

    Fields:
        ticker      - Stock ticker symbol requested by the user (e.g., "AAPL").
        start       - Normalized start date (ISO string) for the queried period.
        end         - Normalized end date (ISO string) for the queried period.
        count       - Number of trading days included in the data range.
        high        - Highest price observed in the period.
        low         - Lowest price observed in the period.
        avg_close   - Average closing price across all returned days.
        last_close  - Closing price of the most recent day in the period.
    """
    ticker: str                           # Requested ticker symbol
    start: str                            # Start date (ISO formatted)
    end: str                              # End date (ISO formatted)
    count: int                            # Number of price entries returned
    high: float                           # Maximum high price in the period
    low: float                            # Minimum low price in the period
    avg_close: float                      # Mean of all closing prices
    last_close: Optional[float] = None    # Closing price on the last available day
