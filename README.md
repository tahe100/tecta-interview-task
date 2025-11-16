# 📈 Stock Stats API

A simple REST API built with **FastAPI**, providing historical stock price statistics fetched dynamically from **yfinance**.  
The project includes **caching**, **unit tests**, a **Dockerfile**, and a short outline for **CI/CD deployment**.

---

## 🚀 Features

- Retrieve **historical OHLCV data** for any stock ticker (e.g., `MSFT`)
- Optional time range support:

```bash
/api/stats?ticker=MSFT&start=2023-01-01&end=2023-12-31
```

- Computes:
  - Highest price
  - Lowest price
  - Average closing price
  - Last closing price
  - Number of trading days

- Gracefully handles:
  - Invalid tickers
  - Empty date ranges
  - Upstream/yfinance errors (returns HTTP 400)

- Includes **pytest** testing with **monkeypatch**
- Fully containerized with **Docker**

---

## 📁 Project Structure

```bash
tecta-interview-task/
│
├── app/
│   ├── main.py        # FastAPI entrypoint
│   ├── models.py      # Pydantic response models
│   ├── services.py    # Business logic + yfinance + caching
│   └── cache.py       # Simple in-memory cache
│
├── tests/
│   ├── test_api.py    # Unit tests (mocked yfinance)
│   └── conftest.py
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧪 Run Locally

### 1. Create environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start API

```bash
uvicorn app.main:app --port 8000
```

### 4. Example request

```bash
http://localhost:8000/api/stats?ticker=MSFT&start=2023-01-01&end=2023-12-31
```

---

## 🧪 Run Tests

```bash
python -m pytest -q 
```

Tests use **monkeypatch**, so **no real network calls** occur.

---

## 🐳 Run with Docker

### 1. Build image

```bash
docker build -t tecta-stats-api .
```

### 2. Run container

```bash
docker run --rm -p 8000:8000 tecta-stats-api
```

### 3. Test endpoint

```bash
http://localhost:8000/api/stats?ticker=MSFT
```

Docker ensures a clean, portable environment across all machines.

---

## 📘 API Endpoints

### GET `/api/health`

Health check endpoint.

#### Response

```json
{
  "status": "ok"
}
```

---

### GET `/api/stats`

```bash
/api/stats?ticker=MSFT&start=YYYY-MM-DD&end=YYYY-MM-DD
```

| Parameter | Required | Description                        |
|-----------|----------|------------------------------------|
| ticker    | Yes      | Stock ticker (e.g., MSFT)          |
| start     | No       | Start date (default: end - 365 days) |
| end       | No       | End date (default: today)          |

#### Example response

```json
{
  "ticker": "MSFT",
  "start": "2023-01-01",
  "end": "2023-12-31",
  "count": 250,
  "high": 379.36,
  "low": 214.62,
  "avg_close": 308.71,
  "last_close": 371.21
}
```

---

## ⚙️ Error Handling

| Case                     | Behavior         |
|--------------------------|------------------|
| Invalid ticker           | API returns 404  |
| Upstream error (yfinance crash) | API returns 400  |
| `start > end`            | API returns 400  |

All error cases are covered in unit tests.