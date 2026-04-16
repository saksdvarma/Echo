from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioState:
    cash: float
    position_qty: int
    avg_entry_price: float
    peak_equity: float
    last_price: float

    @property
    def equity(self) -> float:
        return self.cash + (self.position_qty * self.last_price)

    @property
    def drawdown(self) -> float:
        if self.peak_equity <= 0:
            return 0.0
        return max(0.0, (self.peak_equity - self.equity) / self.peak_equity)


class RiskManager:
    def __init__(self, max_position_size: int, max_daily_drawdown: float, stop_loss_pct: float):
        self.max_position_size = max_position_size
        self.max_daily_drawdown = max_daily_drawdown
        self.stop_loss_pct = stop_loss_pct

    def circuit_breaker_triggered(self, state: PortfolioState) -> bool:
        return state.drawdown >= self.max_daily_drawdown

    def stop_loss_triggered(self, state: PortfolioState) -> bool:
        if state.position_qty <= 0 or state.avg_entry_price <= 0:
            return False
        loss_pct = (state.avg_entry_price - state.last_price) / state.avg_entry_price
        return loss_pct >= self.stop_loss_pct

    def clamp_order_size(self, desired_qty: int, state: PortfolioState) -> int:
        target_position = state.position_qty + desired_qty
        if target_position > self.max_position_size:
            return self.max_position_size - state.position_qty
        if target_position < 0:
            return -state.position_qty
        return desired_qty
