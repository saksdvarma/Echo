# Echo: AI-Powered Algorithmic Trading

Quantitative trading prototype that combines time-series forecasting with real-time sentiment to produce risk-aware execution signals.

## Portfolio Snapshot

- **Project type**: Applied ML + backend systems
- **Primary goal**: Demonstrate end-to-end design of a sentiment-aware trading engine
- **Stack**: Python, FastAPI, NumPy/Pandas, PyTorch-compatible modeling, Docker
- **Core themes**: modeling, API design, risk controls, simulation, reproducible local deployment

## Why This Project Matters

Traditional technical models often miss abrupt sentiment-driven moves. Echo is built to show how market micro-signals (news/headlines) can be fused with price forecasting while preserving disciplined risk management:

- forecast market direction with an LSTM-based time-series model,
- score market tone using NLP-inspired sentiment weighting,
- execute only when combined signal confidence exceeds a threshold,
- enforce portfolio guardrails via drawdown circuit breaker and stop-loss checks.

## System Capabilities

- **Forecasting**: `LSTMForecaster` with PyTorch path and deterministic fallback path.
- **Sentiment analysis**: `TransformerSentimentAnalyzer` weighted polarity/confidence scoring.
- **Signal engine**: confidence-aware blend of model output and sentiment score.
- **Risk layer**: max drawdown halt, stop-loss liquidation, and position-size clamping.
- **Broker simulation**: paper-trading order execution with portfolio accounting.
- **Service layer**: FastAPI endpoints for signaling, state introspection, and backtesting.
- **Operational setup**: local + Docker execution paths with environment-based config.

## Architecture

```text
Price + Headline Tick
         |
         v
  +------------------+      +----------------------+
  | LSTM Forecaster  |----->|                      |
  +------------------+      |   Signal Composer    |----+
                            | (forecast + sentiment)    |
  +------------------+      |                      |    |
  | Sentiment Model  |----->|                      |    |
  +------------------+      +----------------------+    |
                                                        v
                                           +------------------------+
                                           | Risk Manager           |
                                           | - drawdown breaker     |
                                           | - stop loss            |
                                           | - position limits      |
                                           +------------------------+
                                                        |
                                                        v
                                           +------------------------+
                                           | Paper Broker / Orders  |
                                           +------------------------+
                                                        |
                                                        v
                                              Portfolio + API state
```

## API Endpoints

- `GET /health` - service health check
- `GET /state` - current pipeline and portfolio state
- `POST /signal` - run a single tick through the decision engine
- `POST /backtest?steps=<n>` - synthetic simulation over `n` steps

## Quickstart

### 1) Install

```bash
python -m venv .venv
# PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Optional ML extras:

```bash
python -m pip install -e ".[ml]"
```

### 2) Configure

```bash
copy .env.example .env
```

Update runtime values in `.env` as needed.

### 3) Run API

```bash
python -m uvicorn echo.api.main:app --reload --app-dir src
```

Open `http://127.0.0.1:8000/docs`.

### 4) Run local simulation

```bash
python scripts/run_pipeline.py
```

### 5) Validate

```bash
python -m ruff check .
python -m pytest -q
```

## Docker

```bash
docker compose up --build
```

Service is available at `http://localhost:8000`.

## Repository Guide

- `src/echo/models/lstm.py` - time-series model implementation
- `src/echo/models/sentiment.py` - sentiment scoring engine
- `src/echo/strategy.py` - signal composition logic
- `src/echo/risk.py` - risk constraints and safeguards
- `src/echo/broker.py` - paper broker and order accounting
- `src/echo/pipeline.py` - orchestration layer
- `src/echo/api/main.py` - API entrypoint
- `tests/` - baseline behavior tests

## Extended Documentation

- `docs/PROJECT_REPORT.md` - recruiter-ready project report
- `docs/ENGINEERING_NOTES.md` - technical design decisions and trade-offs
- `docs/OPERATIONS.md` - runbook, validation, and troubleshooting

## Future Production Upgrades

- Replace lexicon fallback with transformer inference (FinBERT/DeBERTa).
- Integrate real broker and market/news provider adapters.
- Add persistent telemetry and latency SLO monitoring.
- Add experiment tracking and scheduled model retraining workflow.
