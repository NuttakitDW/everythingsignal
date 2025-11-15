import json
import pandas as pd

from .backtester import run_backtest
from .serialization import build_model_artifact

# 1) Fake data
dates = pd.date_range("2020-01-01", periods=100)
df = pd.DataFrame(
    {
        "open": range(100),
        "high": [x + 1 for x in range(100)],
        "low": [x - 1 for x in range(100)],
        "close": [x + 0.5 for x in range(100)],
        "volume": [1000 + 10 * x for x in range(100)],
    },
    index=dates,
)

# 2) ESL model (JSON operator tree)
model_json = {
    "op": "SUB",
    "args": [
        {"op": "SMA", "args": ["close", 10]},
        {"op": "SMA", "args": ["close", 30]},
    ],
}

# 3) Backtest
result = run_backtest(model_json, df)

# 4) Build artifact with some metadata
metadata = {
    "name": "SMA Spread 10–30",
    "description": "Simple momentum model using SMA spread.",
    "tags": ["momentum", "sma"],
    "universe": "single_asset",
    "symbol": "DEMO",
    "author_id": "example-user",
}

artifact = build_model_artifact(model_json, result, metadata=metadata)

# 5) Convert to JSON text (ready to store or upload to Walrus)
artifact_json_str = json.dumps(artifact, indent=2)
print(artifact_json_str[:500], "...")
