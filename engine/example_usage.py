# engine/example_usage.py

from __future__ import annotations

import numpy as np
import pandas as pd

from .executor import evaluate_expression_tree


def make_dummy_data(n: int = 100) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = np.cumsum(np.random.randn(n)) + 100.0

    df = pd.DataFrame(
        {
            "open": prices + np.random.randn(n) * 0.3,
            "high": prices + np.abs(np.random.randn(n)),
            "low": prices - np.abs(np.random.randn(n)),
            "close": prices + np.random.randn(n) * 0.2,
            "volume": np.random.randint(1_000, 10_000, size=n),
        },
        index=idx,
    )
    return df


def main() -> None:
    data = make_dummy_data()

    # ESL JSON model:
    # SMA(close, 20) - SMA(close, 50)
    tree = {
        "op": "SUB",
        "args": [
            {"op": "SMA", "args": ["close", 20]},
            {"op": "SMA", "args": ["close", 50]},
        ],
    }

    signal = evaluate_expression_tree(tree, data)

    print("Signal (head):")
    print(signal.head(15))

    # Another example:
    # NORMALIZE( DIFF(close, 5) ) * NORMALIZE(volume)
    composite_tree = {
        "op": "MUL",
        "args": [
            {
                "op": "NORMALIZE",
                "args": [
                    {"op": "DIFF", "args": ["close", 5]},
                ],
            },
            {
                "op": "NORMALIZE",
                "args": ["volume"],
            },
        ],
    }

    signal2 = evaluate_expression_tree(composite_tree, data)
    print("\nComposite signal (head):")
    print(signal2.head(15))


if __name__ == "__main__":
    main()
