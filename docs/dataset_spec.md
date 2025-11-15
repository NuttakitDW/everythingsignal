# 📊 EverythingSignal Dataset Specification (v0.1)
**Dataset:** BTC–USDT, 1-Day Candles  
**Date Range:** 2018-01-01 → 2024-01-01  
**Timezone:** UTC  
**Framework Version:** Dataset v0.1  
**File Format:** CSV (canonical), Parquet (optional)

---

## 1. Purpose of This Dataset

EverythingSignal requires a **deterministic, canonical dataset** so that:

- Backtests are reproducible.
- ZK proofs can commit to a verified dataset hash.
- Engine behavior is identical across machines.
- Marketplace buyers trust performance metrics.

This dataset is the **only allowed input** for model evaluation in EverythingSignal v0.1.

---

## 2. Data Schema (Canonical)

The dataset MUST contain exactly the following columns:

| Column     | Type      | Description                                    |
|------------|-----------|------------------------------------------------|
| timestamp  | string    | ISO8601 UTC (`YYYY-MM-DD`)                     |
| open       | float     | Opening price of BTC-USDT                      |
| high       | float     | Highest price of the day                       |
| low        | float     | Lowest price of the day                        |
| close      | float     | Closing price of the day                       |
| volume     | float     | Total traded volume (normalized)               |

---

## 3. Canonical Rules

### 3.1 Timestamp Format
```
YYYY-MM-DD
```
(no time component)

### 3.2 Sorting
Rows must be sorted in strictly ascending timestamp order.

### 3.3 Missing Data Handling
- No missing rows
- No empty fields
- No NaNs allowed

If a real-world dataset contains holes, they must be filled using:
- previous-day forward fill (prices)
- zero fill (volume)

---

## 4. Dataset Hashing

### 4.1 Canonical CSV String
Hash is computed over:

```
timestamp,open,high,low,close,volume\n
2018-01-01,OPEN, HIGH, LOW, CLOSE, VOLUME\n
...
2024-01-01,OPEN, HIGH, LOW, CLOSE, VOLUME
```

No trailing newline at the end of file.

### 4.2 Hash Algorithm
```
SHA-256(canonical_csv_bytes)
```

### 4.3 Example Hash Field in Artifact
```json
{
  "id": "btc-usdt-1d-v0.1",
  "hash": "c83e3cc3cf77c...f199e8",
  "timeframe": "1D",
  "symbol": "BTC-USDT"
}
```

---

## 5. Storage & Distribution

The dataset will be stored:

* in the GitHub repo under `data/btc_usdt_1d.csv`
* optionally on Walrus for immutability

---

## 6. Versioning Policy

Any change to:

* date range
* symbol
* timeframe
* filling rules

→ produces a new **dataset version**: `v0.2`.

---

This dataset spec is final for EverythingSignal v0.1.