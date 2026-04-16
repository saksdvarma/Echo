from __future__ import annotations

from dataclasses import dataclass

from .risk import PortfolioState


@dataclass(slots=True)
class Order:
    symbol: str
    side: str
    qty: int
    price: float


class PaperBroker:
    def __init__(self, initial_cash: float):
        self.state = PortfolioState(
            cash=initial_cash,
            position_qty=0,
            avg_entry_price=0.0,
            peak_equity=initial_cash,
            last_price=0.0,
        )
        self.orders: list[Order] = []

    def update_mark(self, price: float) -> None:
        self.state.last_price = price
        self.state.peak_equity = max(self.state.peak_equity, self.state.equity)

    def execute_market(self, symbol: str, side: str, qty: int, price: float) -> None:
        if qty <= 0:
            return
        self.update_mark(price)
        if side == "buy":
            self._buy(symbol, qty, price)
        elif side == "sell":
            self._sell(symbol, qty, price)
        else:
            raise ValueError(f"Unsupported side: {side}")

    def _buy(self, symbol: str, qty: int, price: float) -> None:
        cost = qty * price
        if cost > self.state.cash:
            qty = int(self.state.cash // price)
            cost = qty * price
        if qty <= 0:
            return
        new_position = self.state.position_qty + qty
        weighted_cost = (self.state.position_qty * self.state.avg_entry_price) + cost
        self.state.position_qty = new_position
        self.state.avg_entry_price = weighted_cost / new_position
        self.state.cash -= cost
        self.orders.append(Order(symbol=symbol, side="buy", qty=qty, price=price))

    def _sell(self, symbol: str, qty: int, price: float) -> None:
        qty = min(qty, self.state.position_qty)
        if qty <= 0:
            return
        proceeds = qty * price
        self.state.position_qty -= qty
        self.state.cash += proceeds
        if self.state.position_qty == 0:
            self.state.avg_entry_price = 0.0
        self.orders.append(Order(symbol=symbol, side="sell", qty=qty, price=price))
