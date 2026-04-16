# Operations Runbook

## Prerequisites

- Python 3.10+
- Optional Docker Desktop

## Local Startup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
copy .env.example .env
python -m uvicorn echo.api.main:app --reload --app-dir src
```

## Health and Validation Commands

```bash
python -m ruff check .
python -m pytest -q
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/state"
```

## Sample Signal Request (PowerShell)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/signal" `
  -ContentType "application/json" `
  -Body '{"price":101.35,"headlines":["Company beat earnings and strong growth guidance"]}'
```

## Docker Run

```bash
docker compose up --build
```

## Common Issues

- **`pytest` not found**
  - Run `python -m pip install -e ".[dev]"`.
- **`uvicorn` not found in PATH**
  - Run with module form: `python -m uvicorn ...`.
- **Missing environment file**
  - Ensure `.env` exists (copy from `.env.example`).

## Safe Demo Checklist

- Lint clean.
- Tests passing.
- `/health` returns `ok`.
- `/signal` returns structured decision payload.
- `/backtest` returns final-step summary.
