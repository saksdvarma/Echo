# Engineering Notes

## Core Modules

- `config.py`: typed environment-based runtime settings.
- `data.py`: market tick models and synthetic feed generation.
- `models/lstm.py`: LSTM forecaster with optional PyTorch path + fallback.
- `models/sentiment.py`: sentiment scoring and confidence weighting.
- `strategy.py`: composite signal decision logic.
- `risk.py`: stop-loss, drawdown checks, and sizing constraints.
- `broker.py`: paper execution and portfolio accounting.
- `pipeline.py`: orchestration across all modules.
- `api/main.py`: REST endpoints and service wiring.

## Decision Rules

1. Compute forecast return and confidence.
2. Compute sentiment score from headlines.
3. Blend scores into one composite decision metric.
4. Emit `buy`, `sell`, or `hold` against configurable threshold.
5. Clamp order size and block trades if risk constraints fail.

## Configuration Model

All runtime controls are environment-driven through `EchoSettings`:

- `ECHO_SYMBOL`
- `ECHO_LOOKBACK_WINDOW`
- `ECHO_SENTIMENT_WEIGHT`
- `ECHO_PREDICTION_THRESHOLD`
- `ECHO_MAX_POSITION_SIZE`
- `ECHO_MAX_DAILY_DRAWDOWN`
- `ECHO_STOP_LOSS_PCT`
- `ECHO_INITIAL_CASH`

## Testing Strategy

- **Unit tests** focus on deterministic business logic:
  - strategy threshold behavior,
  - sentiment polarity direction,
  - risk clamping and breaker conditions.
- **Smoke tests** validate runtime behavior through API endpoints.
- **Lint checks** enforce import style and code hygiene.

## Extension Strategy

- Replace synthetic tick feed with real adapters while preserving `MarketTick` schema.
- Add structured logging for decision observability.
- Add asynchronous ingestion path for high-frequency streams.
- Add historical replay backtests with transaction-cost modeling.
