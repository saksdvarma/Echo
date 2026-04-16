from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    TORCH_AVAILABLE = False
    torch = None
    nn = None


@dataclass(slots=True)
class ForecastResult:
    expected_return: float
    confidence: float


class _TorchLSTM(nn.Module):  # type: ignore[misc]
    def __init__(self, input_size: int = 1, hidden_size: int = 16):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.head = nn.Linear(hidden_size, 1)

    def forward(self, x):  # type: ignore[override]
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


class LSTMForecaster:
    """
    Time-series forecaster built around LSTM architecture.

    Uses PyTorch when available; otherwise falls back to a deterministic
    momentum baseline so the app remains executable in lightweight setups.
    """

    def __init__(self, lookback_window: int = 32):
        self.lookback_window = lookback_window
        self._is_trained = False
        self._device = "cpu"
        self._model = _TorchLSTM() if TORCH_AVAILABLE else None

    def fit(self, closes: list[float], epochs: int = 8, lr: float = 1e-3) -> None:
        if len(closes) <= self.lookback_window + 1:
            self._is_trained = False
            return
        if not TORCH_AVAILABLE:
            self._is_trained = True
            return

        x_data, y_data = self._build_windows(closes)
        x_tensor = torch.tensor(x_data, dtype=torch.float32).unsqueeze(-1)
        y_tensor = torch.tensor(y_data, dtype=torch.float32).unsqueeze(-1)
        optimizer = torch.optim.Adam(self._model.parameters(), lr=lr)
        loss_fn = nn.MSELoss()
        self._model.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            preds = self._model(x_tensor)
            loss = loss_fn(preds, y_tensor)
            loss.backward()
            optimizer.step()
        self._is_trained = True

    def predict_return(self, closes: list[float]) -> ForecastResult:
        if len(closes) < self.lookback_window + 1:
            return ForecastResult(expected_return=0.0, confidence=0.1)
        if not self._is_trained:
            self.fit(closes)
        if not TORCH_AVAILABLE:
            return self._fallback_prediction(closes)

        recent = np.array(closes[-self.lookback_window :], dtype=float)
        start_price = float(recent[-1])
        model_input = torch.tensor(recent, dtype=torch.float32).view(1, -1, 1)
        self._model.eval()
        with torch.no_grad():
            pred_price = float(self._model(model_input)[0][0].item())
        expected_return = ((pred_price / max(start_price, 1e-6)) - 1.0) * 0.5
        normalized_vol = min(1.0, float(np.std(np.diff(recent))) / max(start_price * 0.02, 1e-6))
        confidence = max(0.1, 1.0 - normalized_vol)
        return ForecastResult(expected_return=expected_return, confidence=confidence)

    def _build_windows(self, closes: list[float]) -> tuple[np.ndarray, np.ndarray]:
        arr = np.array(closes, dtype=np.float32)
        windows = []
        targets = []
        for i in range(len(arr) - self.lookback_window):
            window = arr[i : i + self.lookback_window]
            target = arr[i + self.lookback_window]
            windows.append(window)
            targets.append(target)
        return np.array(windows), np.array(targets)

    def _fallback_prediction(self, closes: list[float]) -> ForecastResult:
        recent = np.array(closes[-self.lookback_window :], dtype=float)
        rets = np.diff(recent) / np.clip(recent[:-1], 1e-6, None)
        expected_return = float(np.mean(rets[-5:])) if len(rets) >= 5 else float(np.mean(rets))
        confidence = max(0.1, 1.0 - min(0.9, float(np.std(rets) * 25)))
        return ForecastResult(expected_return=expected_return, confidence=confidence)
