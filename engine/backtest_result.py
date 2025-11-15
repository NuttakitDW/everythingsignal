from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class BacktestResult:
    signal: pd.Series
    strategy_returns: pd.Series
    cumulative_returns: pd.Series
    metrics: Dict[str, float]
