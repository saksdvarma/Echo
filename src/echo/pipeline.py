from __future__ import annotations

from dataclasses import asdict, dataclass

from .broker import PaperBroker
from .config import EchoSettings
from .data import MarketTick
from .models.lstm import LSTMForecaster
from .models.sentiment import TransformerSentimentAnalyzer
from .risk import RiskManager
from .strategy import EchoStrategy


@dataclass(slots=True)
class StepResult:
    signal: str
    score: float
    sentiment: float
    forecast_return: float
    forecast_confidence: float
    equity: float
    drawdown: float
    halted: bool


class EchoPipeline:
    def __init__(self, settings: EchoSettings):
        self.settings = settings
        self.closes: list[float] = []
        self.forecaster = LSTMForecaster(lookback_window=settings.lookback_window)
        self.sentiment = TransformerSentimentAnalyzer()
        self.strategy = EchoStrategy(settings)
        self.broker = PaperBroker(settings.initial_cash)
        self.risk = RiskManager(
            max_position_size=settings.max_position_size,
            max_daily_drawdown=settings.max_daily_drawdown,
            stop_loss_pct=settings.stop_loss_pct,
        )

    def step(self, tick: MarketTick) -> StepResult:
        self.closes.append(tick.price)
        self.broker.update_mark(tick.price)

        state = self.broker.state
        if self.risk.circuit_breaker_triggered(state):
            return self._result("hold", 0.0, 0.0, 0.0, 0.0, halted=True)

        if self.risk.stop_loss_triggered(state):
            qty = self.risk.clamp_order_size(-state.position_qty, state)
            if qty < 0:
                self.broker.execute_market(self.settings.symbol, "sell", abs(qty), tick.price)
            return self._result("sell", -1.0, 0.0, 0.0, 1.0, halted=False)

        forecast = self.forecaster.predict_return(self.closes)
        sentiment_score = self.sentiment.batch_score(tick.headlines)
        decision = self.strategy.decide(
            forecast_return=forecast.expected_return,
            forecast_confidence=forecast.confidence,
            sentiment_score=sentiment_score,
        )

        order_qty = self._size_order(decision.signal, abs(decision.score))
        if decision.signal == "buy" and order_qty > 0:
            allowed = self.risk.clamp_order_size(order_qty, self.broker.state)
            self.broker.execute_market(self.settings.symbol, "buy", max(allowed, 0), tick.price)
        elif decision.signal == "sell" and order_qty > 0:
            allowed = self.risk.clamp_order_size(-order_qty, self.broker.state)
            self.broker.execute_market(self.settings.symbol, "sell", abs(min(allowed, 0)), tick.price)

        return self._result(
            decision.signal,
            decision.score,
            sentiment_score,
            forecast.expected_return,
            forecast.confidence,
            halted=False,
        )

    def _size_order(self, signal: str, confidence_score: float) -> int:
        if signal == "hold":
            return 0
        base = max(1, int(self.settings.max_position_size * min(1.0, confidence_score)))
        return base

    def _result(
        self,
        signal: str,
        score: float,
        sentiment: float,
        forecast_return: float,
        forecast_confidence: float,
        halted: bool,
    ) -> StepResult:
        state = self.broker.state
        self.broker.update_mark(state.last_price)
        return StepResult(
            signal=signal,
            score=score,
            sentiment=sentiment,
            forecast_return=forecast_return,
            forecast_confidence=forecast_confidence,
            equity=state.equity,
            drawdown=state.drawdown,
            halted=halted,
        )

    def as_dict(self) -> dict:
        state = self.broker.state
        return {
            "config": self.settings.model_dump(),
            "portfolio": asdict(state),
            "orders": [asdict(o) for o in self.broker.orders],
            "bars_seen": len(self.closes),
        }
