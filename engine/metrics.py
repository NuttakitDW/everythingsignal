# engine/metrics.py

import numpy as np
import pandas as pd


def _clean(series: pd.Series) -> pd.Series:
    """Remove NaN and infinite values before computing metrics."""
    return series.replace([np.inf, -np.inf], np.nan).dropna()


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = _clean(returns)
    if len(r) == 0:
        return 0.0
    mean = r.mean()
    std = r.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float((mean / std) * np.sqrt(periods_per_year))


def volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = _clean(returns)
    if len(r) == 0:
        return 0.0
    return float(r.std() * np.sqrt(periods_per_year))


def max_drawdown(returns: pd.Series) -> float:
    r = _clean(returns)
    if len(r) == 0:
        return 0.0
    equity = (1 + r).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def cagr(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = _clean(returns)
    if len(r) == 0:
        return 0.0

    total_return = float((1 + r).prod() - 1.0)

    days = (r.index[-1] - r.index[0]).days
    if days <= 0:
        return 0.0

    years = days / 365.25
    if years <= 0:
        return 0.0

    return float((1 + total_return) ** (1 / years) - 1)


def win_rate(returns: pd.Series) -> float:
    r = _clean(returns)
    if len(r) == 0:
        return 0.0
    return float((r > 0).sum() / len(r))
