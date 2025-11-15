from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

import pandas as pd
from datetime import datetime, timezone

from .backtest_result import BacktestResult


def series_to_json(series: pd.Series) -> Dict[str, Any]:
    """
    Serialize a Pandas Series with DatetimeIndex into
    { "index": [...], "values": [...] } format.
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        # Best effort: try to convert
        idx = pd.to_datetime(series.index)
    else:
        idx = series.index

    index = [ts.isoformat() for ts in idx]
    values = [float(x) if pd.notna(x) else None for x in series.to_list()]

    return {
        "index": index,
        "values": values,
    }


def series_from_json(obj: Dict[str, Any]) -> pd.Series:
    """
    Reverse of series_to_json. Not strictly needed for Walrus storage,
    but useful if you want to reconstruct BacktestResult later.
    """
    index = pd.to_datetime(obj["index"])
    values = obj["values"]
    return pd.Series(values, index=index, dtype="float64")


def backtest_result_to_json(
    result: BacktestResult,
    include_signal: bool = True,
    include_strategy_returns: bool = True,
    include_cumulative_returns: bool = True,
) -> Dict[str, Any]:
    """
    Serialize BacktestResult into JSON-serializable dict.
    """
    backtest_json: Dict[str, Any] = {
        "metrics": {k: float(v) for k, v in result.metrics.items()}
    }

    if include_signal:
        backtest_json["signal"] = series_to_json(result.signal)

    if include_strategy_returns:
        backtest_json["strategy_returns"] = series_to_json(
            result.strategy_returns
        )

    if include_cumulative_returns:
        backtest_json["cumulative_returns"] = series_to_json(
            result.cumulative_returns
        )

    return backtest_json


def build_model_artifact(
    model_json: Dict[str, Any],
    backtest_result: BacktestResult,
    metadata: Optional[Dict[str, Any]] = None,
    esl_version: str = "0.1",
    engine_version: str = "0.1",
    schema_version: str = "esl-artifact-0.1",
) -> Dict[str, Any]:
    """
    Build the full EverythingSignal model artifact payload.

    This is the object you will:
      - store as JSON
      - upload to Walrus
      - return via API
    """
    if metadata is None:
        metadata = {}

    created_at = datetime.now(timezone.utc).isoformat()

    artifact: Dict[str, Any] = {
        "schema_version": schema_version,
        "esl_version": esl_version,
        "engine_version": engine_version,
        "created_at": created_at,
        "model": model_json,
        "backtest": backtest_result_to_json(backtest_result),
        "metadata": metadata,
    }

    return artifact
