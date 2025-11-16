# engine/artifacts.py

import json
import math
from typing import Any, Dict

from .dataset_hash import get_dataset_hash


ENGINE_VERSION = "0.1"
ESL_VERSION = "0.1"
DATASET_VERSION = "0.1"
DATASET_ID = "btc-usdt-1d-v0.1"


def _pandas_series_to_json(series):
    """Convert pandas Series to deterministic JSON format."""
    if series is None:
        return None

    index = []
    values = []

    for ts, v in series.items():
        # Convert timestamp → ISO string
        index.append(ts.isoformat())

        # Convert NaN → None
        if isinstance(v, float) and math.isnan(v):
            values.append(None)
        else:
            values.append(v)

    return {
        "index": index,
        "values": values
    }


def _metrics_to_json(metrics: Dict[str, float]):
    """Ensure all metrics are JSON serializable and NaN-safe."""
    out = {}
    for k, v in metrics.items():
        if isinstance(v, float) and math.isnan(v):
            out[k] = None
        else:
            out[k] = v
    return out


def build_artifact(model_tree: Dict[str, Any], backtest_result):
    """
    Build the full artifact dictionary for v0.2.

    Parameters:
        model_tree: dict (the ESL JSON operator tree)
        backtest_result: BacktestResult instance

    Returns:
        dict representing the full artifact (ready to upload to Walrus)
    """

    dataset_hash = get_dataset_hash()

    artifact = {
        "version": "0.2",

        "model": model_tree,

        "backtest": {
            "metrics": _metrics_to_json(backtest_result.metrics),
            "signal": _pandas_series_to_json(backtest_result.signal),
            "strategy_returns": _pandas_series_to_json(backtest_result.strategy_returns),
            "cumulative_returns": _pandas_series_to_json(backtest_result.cumulative_returns)
        },

        "dataset": {
            "id": DATASET_ID,
            "hash": dataset_hash,
            "symbol": "BTC-USDT",
            "timeframe": "1D",
            "range": "2018-01-01 to 2024-01-01"
        },

        "zk": {
            "proof_system": "risc0",
            "program_id": None,       # filled in Step 7–8
            "proof": None,            # filled after guest execution
            "public_journal": None    # filled after guest execution
        },

        "metadata": {
            "engine_version": ENGINE_VERSION,
            "esl_version": ESL_VERSION,
            "dataset_version": DATASET_VERSION
        }
    }

    return artifact


def artifact_to_json_bytes(artifact: Dict[str, Any]) -> bytes:
    """
    Convert the artifact to canonical JSON bytes (sorted keys, no spaces)
    for hashing and Walrus upload.
    """
    return json.dumps(
        artifact,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")
