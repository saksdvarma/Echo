from echo.config import EchoSettings
from echo.strategy import EchoStrategy


def test_buy_signal_when_composite_positive() -> None:
    strategy = EchoStrategy(EchoSettings(prediction_threshold=0.001))
    decision = strategy.decide(forecast_return=0.01, forecast_confidence=0.9, sentiment_score=0.3)
    assert decision.signal == "buy"


def test_hold_signal_when_score_small() -> None:
    strategy = EchoStrategy(EchoSettings(prediction_threshold=0.05))
    decision = strategy.decide(forecast_return=0.01, forecast_confidence=0.2, sentiment_score=0.01)
    assert decision.signal == "hold"
