import pandas as pd

DATASET_PATH = "data/btc_usdt_1d.csv"

REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

def load_dataset() -> pd.DataFrame:
    """Loads and validates the canonical dataset."""
    df = pd.read_csv(DATASET_PATH)

    # Validate columns
    if list(df.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Dataset must have columns: {REQUIRED_COLUMNS}")

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d", utc=True)
    df = df.set_index("timestamp")

    # Validate sorting
    if not df.index.is_monotonic_increasing:
        raise ValueError("Dataset timestamps must be strictly increasing")

    # Validate no NAs
    if df.isna().any().any():
        raise ValueError("Dataset contains NaN values, which are not allowed")

    return df
