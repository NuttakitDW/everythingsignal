# engine/test_operator_tree.py

from __future__ import annotations

import numpy as np
import pandas as pd

from .executor import evaluate_expression_tree


def _make_test_data() -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    prices = pd.Series(np.arange(10, 20), index=idx)
    df = pd.DataFrame(
        {
            "open": prices + 0.5,
            "high": prices + 1.0,
            "low": prices - 1.0,
            "close": prices,
            "volume": np.arange(100, 110),
        },
        index=idx,
    )
    return df


def test_sma_basic():
    df = _make_test_data()
    tree = {"op": "SMA", "args": ["close", 3]}
    signal = evaluate_expression_tree(tree, df)

    assert isinstance(signal, pd.Series)
    assert signal.index.equals(df.index)
    # First 2 values should be NaN due to min_periods=3
    assert signal.iloc[0:2].isna().all()
    # Third value should be mean of close[0:3] = (10 + 11 + 12) / 3
    assert np.isclose(signal.iloc[2], (10 + 11 + 12) / 3)


def test_diff_basic():
    df = _make_test_data()
    tree = {"op": "DIFF", "args": ["close", 1]}
    signal = evaluate_expression_tree(tree, df)

    assert np.isnan(signal.iloc[0])
    # Since close is an increasing sequence by 1, diff(1) should be 1
    assert (signal.iloc[1:] == 1).all()


def test_composite_expression():
    df = _make_test_data()
    tree = {
        "op": "MUL",
        "args": [
            {"op": "NORMALIZE", "args": ["close"]},
            {"op": "NORMALIZE", "args": ["volume"]},
        ],
    }

    signal = evaluate_expression_tree(tree, df)
    assert isinstance(signal, pd.Series)
    assert signal.index.equals(df.index)


if __name__ == "__main__":
    # Simple manual test runner
    test_sma_basic()
    test_diff_basic()
    test_composite_expression()
    print("All tests passed.")
