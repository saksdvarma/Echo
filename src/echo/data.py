from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from random import gauss
from typing import Iterable

import pandas as pd


@dataclass(slots=True)
class MarketTick:
    timestamp: datetime
    price: float
    headlines: list[str]


def load_price_series(csv_path: str) -> pd.DataFrame:
    """Load OHLCV data with a standard 'close' column."""
    df = pd.read_csv(csv_path)
    if "close" not in df.columns:
        raise ValueError("CSV must include a 'close' column.")
    return df


def synthetic_ticks(
    steps: int = 200,
    start_price: float = 100.0,
    base_news: Iterable[str] | None = None,
) -> list[MarketTick]:
    """Generate synthetic market ticks for local testing."""
    base_news = list(base_news or ("Market stable", "Earnings watch", "Macro risk easing"))
    ticks: list[MarketTick] = []
    price = start_price
    now = datetime.utcnow()
    for i in range(steps):
        drift = 0.03
        shock = gauss(0, 0.9)
        price = max(1.0, price + drift + shock)
        ticks.append(
            MarketTick(
                timestamp=now,
                price=round(price, 4),
                headlines=[base_news[i % len(base_news)]],
            )
        )
    return ticks
