# api/config.py

from engine.dataset_hash import get_dataset_hash

DATASET_ID = "btc-usdt-1d-v0.1"
DATASET_SYMBOL = "BTC-USDT"
DATASET_TIMEFRAME = "1D"
DATASET_RANGE = "2018-01-01 to 2024-01-01"

DATASET_HASH = get_dataset_hash()

ARTIFACT_VERSION = "0.2"
ESL_VERSION = "0.1"
ENGINE_VERSION = "0.1"
DATASET_VERSION = "0.1"
