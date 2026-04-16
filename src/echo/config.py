from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EchoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ECHO_")

    symbol: str = "SPY"
    lookback_window: int = 32
    sentiment_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    prediction_threshold: float = Field(default=0.002, ge=0.0)
    max_position_size: int = Field(default=100, ge=1)
    max_daily_drawdown: float = Field(default=0.05, ge=0.0)
    stop_loss_pct: float = Field(default=0.02, ge=0.0)
    initial_cash: float = Field(default=100000.0, gt=0.0)
