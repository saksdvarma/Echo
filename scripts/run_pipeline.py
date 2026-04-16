from dataclasses import asdict
from pathlib import Path
import sys

def _bootstrap_src_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> None:
    _bootstrap_src_path()
    from echo.config import EchoSettings
    from echo.data import synthetic_ticks
    from echo.pipeline import EchoPipeline

    settings = EchoSettings()
    pipeline = EchoPipeline(settings)
    for tick in synthetic_ticks(steps=250):
        result = pipeline.step(tick)
    print("Final step:", asdict(result))
    print("Portfolio:", asdict(pipeline.broker.state))
    print("Orders placed:", len(pipeline.broker.orders))


if __name__ == "__main__":
    main()
