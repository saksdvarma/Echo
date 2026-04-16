from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from echo.config import EchoSettings
from echo.data import MarketTick, synthetic_ticks
from echo.pipeline import EchoPipeline


class TickRequest(BaseModel):
    price: float = Field(gt=0)
    headlines: list[str] = Field(default_factory=list)


settings = EchoSettings()
pipeline = EchoPipeline(settings)
app = FastAPI(title="Echo Trading API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/state")
def state() -> dict:
    return pipeline.as_dict()


@app.post("/signal")
def signal(payload: TickRequest) -> dict:
    tick = MarketTick(timestamp=datetime.utcnow(), price=payload.price, headlines=payload.headlines)
    result = pipeline.step(tick)
    return asdict(result)


@app.post("/backtest")
def backtest(steps: int = 200) -> dict:
    local_pipeline = EchoPipeline(settings)
    latest = None
    for tick in synthetic_ticks(steps=steps):
        latest = local_pipeline.step(tick)
    return {
        "final_step": asdict(latest) if latest else None,
        "orders": [asdict(o) for o in local_pipeline.broker.orders],
        "portfolio": asdict(local_pipeline.broker.state),
    }
