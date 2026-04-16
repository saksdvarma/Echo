from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .config import EchoSettings

Signal = Literal["buy", "sell", "hold"]


@dataclass(slots=True)
class SignalDecision:
    signal: Signal
    score: float
    reason: str


class EchoStrategy:
    def __init__(self, settings: EchoSettings):
        self.settings = settings

    def decide(
        self,
        forecast_return: float,
        forecast_confidence: float,
        sentiment_score: float,
    ) -> SignalDecision:
        model_component = forecast_return * forecast_confidence
        sentiment_component = sentiment_score * self.settings.sentiment_weight
        composite = model_component + sentiment_component

        threshold = self.settings.prediction_threshold
        if composite >= threshold:
            return SignalDecision("buy", composite, "Positive forecast + sentiment alignment.")
        if composite <= -threshold:
            return SignalDecision("sell", composite, "Negative forecast + sentiment alignment.")
        return SignalDecision("hold", composite, "Signal confidence below execution threshold.")
