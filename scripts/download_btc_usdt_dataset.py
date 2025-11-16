# scripts/download_btc_usdt_dataset.py

import yfinance as yf
import pandas as pd
from pathlib import Path

OUTPUT_PATH = Path("data/btc_usdt_1d.csv")

def main():
    # 1) Download from Yahoo as BTC-USD
    df = yf.download(
        "BTC-USD",
        start="2018-01-01",
        end="2024-01-02",
        interval="1d",
        auto_adjust=False,
    )

    # 2) Keep only needed columns and rename
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    # 3) Canonical index → timestamp column in YYYY-MM-DD
    df.index = df.index.tz_localize(None)  # drop timezone if any
    df.insert(0, "timestamp", df.index.strftime("%Y-%m-%d"))

    # 4) Ensure no NaNs (simple forward-fill for prices, 0 for volume)
    price_cols = ["open", "high", "low", "close"]
    df[price_cols] = df[price_cols].ffill()
    df["volume"] = df["volume"].fillna(0.0)

    # 5) Sort just in case
    df = df.sort_values("timestamp")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 6) Save canonical CSV (no index, stable float format)
    csv_str = df.to_csv(index=False, float_format="%.8f", lineterminator="\n")
    # Remove trailing newline to match spec
    if csv_str.endswith("\n"):
        csv_str = csv_str[:-1]

    OUTPUT_PATH.write_text(csv_str, encoding="utf-8")
    print(f"Saved canonical dataset to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
