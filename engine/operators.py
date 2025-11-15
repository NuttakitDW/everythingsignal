# engine/operators.py

from __future__ import annotations

from typing import Any, Callable, Dict
import numpy as np
import pandas as pd


Series = pd.Series


def op_ADD(x: Series | float | int, y: Series | float | int) -> Series:
    return x + y


def op_SUB(x: Series | float | int, y: Series | float | int) -> Series:
    return x - y


def op_MUL(x: Series | float | int, y: Series | float | int) -> Series:
    return x * y


def op_DIV(x: Series | float | int, y: Series | float | int) -> Series:
    return x / y


def op_ABS(x: Series | float | int) -> Series:
    return x.abs() if isinstance(x, pd.Series) else abs(x)


def op_LOG(x: Series | float | int) -> Series:
    # Assume x > 0 for meaningful log
    if isinstance(x, pd.Series):
        return np.log(x)
    return float(np.log(x))


def op_SMA(x: Series, n: int) -> Series:
    return x.rolling(window=n, min_periods=n).mean()


def op_EMA(x: Series, n: int) -> Series:
    return x.ewm(span=n, adjust=False).mean()


def op_LAG(x: Series, n: int) -> Series:
    return x.shift(n)


def op_DIFF(x: Series, n: int) -> Series:
    return x - x.shift(n)


def op_RETURN(x: Series, n: int) -> Series:
    shifted = x.shift(n)
    return (x / shifted) - 1.0


def op_NORMALIZE(x: Series) -> Series:
    mean = x.mean()
    std = x.std(ddof=0)
    if std == 0 or np.isnan(std):
        # Avoid division by zero: return zeros series
        return pd.Series(0.0, index=x.index)
    return (x - mean) / std


def op_ROLLING_STD(x: Series, n: int) -> Series:
    return x.rolling(window=n, min_periods=n).std(ddof=0)


def op_ROLLING_MEAN(x: Series, n: int) -> Series:
    # Alias for SMA for clarity
    return op_SMA(x, n)


# Registry mapping operator names to implementation functions
OPERATOR_REGISTRY: Dict[str, Callable[..., Any]] = {
    "ADD": op_ADD,
    "SUB": op_SUB,
    "MUL": op_MUL,
    "DIV": op_DIV,
    "ABS": op_ABS,
    "LOG": op_LOG,
    "SMA": op_SMA,
    "EMA": op_EMA,
    "LAG": op_LAG,
    "DIFF": op_DIFF,
    "RETURN": op_RETURN,
    "NORMALIZE": op_NORMALIZE,
    "ROLLING_STD": op_ROLLING_STD,
    "ROLLING_MEAN": op_ROLLING_MEAN,
}
