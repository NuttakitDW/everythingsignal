# engine/backtester.py

import pandas as pd

from .executor import eval_node
from .backtest_result import BacktestResult
from .metrics import (
    sharpe_ratio,
    volatility,
    max_drawdown,
    cagr,
    win_rate,
)


def run_backtest(model_json, price_df: pd.DataFrame, periods_per_year: int = 252):
    """
    Minimal long/short backtest using lagged signal exposure.
    """

    # --- B4: Evaluate model to generate signal ---
    data_dict = {
        "open": price_df["open"],
        "high": price_df["high"],
        "low": price_df["low"],
        "close": price_df["close"],
        "volume": price_df["volume"],
    }

    signal = eval_node(model_json, data_dict)

    # --- B3: Compute asset returns ---
    asset_returns = price_df["close"].pct_change()

    # --- B5: Align signal and returns by common index ---
    combined_index = signal.index.intersection(asset_returns.index)
    signal = signal.loc[combined_index]
    asset_returns = asset_returns.loc[combined_index]

    # --- B6: Compute exposure (lagged signal, no lookahead) ---
    exposure = signal.shift(1)

    # --- B7: Compute strategy returns ---
    strategy_returns = exposure * asset_returns

    # --- B8: Compute cumulative returns ---
    cumulative_returns = (1 + strategy_returns.fillna(0)).cumprod() - 1.0

    # --- B9: Compute metrics ---
    metrics = {
        "sharpe": sharpe_ratio(strategy_returns, periods_per_year),
        "volatility": volatility(strategy_returns, periods_per_year),
        "max_drawdown": max_drawdown(strategy_returns),
        "cagr": cagr(strategy_returns, periods_per_year),
        "win_rate": win_rate(strategy_returns),
    }

    # --- Final return object ---
    return BacktestResult(
        signal=signal,
        strategy_returns=strategy_returns,
        cumulative_returns=cumulative_returns,
        metrics=metrics,
    )
