from echo.risk import PortfolioState, RiskManager


def test_circuit_breaker_triggered_on_drawdown() -> None:
    manager = RiskManager(max_position_size=100, max_daily_drawdown=0.05, stop_loss_pct=0.02)
    state = PortfolioState(
        cash=5000.0,
        position_qty=100,
        avg_entry_price=100.0,
        peak_equity=11000.0,
        last_price=50.0,
    )
    assert manager.circuit_breaker_triggered(state) is True


def test_order_size_clamped_to_max_position() -> None:
    manager = RiskManager(max_position_size=100, max_daily_drawdown=0.05, stop_loss_pct=0.02)
    state = PortfolioState(
        cash=100000.0,
        position_qty=90,
        avg_entry_price=100.0,
        peak_equity=100000.0,
        last_price=100.0,
    )
    assert manager.clamp_order_size(20, state) == 10
