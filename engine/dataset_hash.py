# engine/dataset_hash.py

import hashlib
import pathlib

DATASET_PATH = pathlib.Path("data/btc_usdt_1d.csv")


def get_dataset_hash() -> str:
    """
    Compute SHA-256 hash over the raw bytes of the canonical dataset CSV.

    Returns:
        str: hex string of the SHA-256 hash
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    raw = DATASET_PATH.read_bytes()

    return hashlib.sha256(raw).hexdigest()
