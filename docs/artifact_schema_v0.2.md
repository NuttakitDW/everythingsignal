# 📦 EverythingSignal Artifact Schema (v0.2)

This schema defines the final, verifiable, publicly-readable artifact stored on Walrus.

Artifact contains:

1. Model definition  
2. Backtest results  
3. Dataset description  
4. ZK verification data  
5. Metadata  

---

## 1. Top-Level Structure

```json
{
  "version": "0.2",
  "model": { ... },
  "backtest": { ... },
  "dataset": { ... },
  "zk": { ... },
  "metadata": { ... }
}
```

---

## 2. `"model"` Block

JSON operator tree from ESL v0.1:

```json
{
  "op": "SUB",
  "args": [
    { "op": "SMA", "args": ["close", 20] },
    { "op": "SMA", "args": ["close", 50] }
  ]
}
```

---

## 3. `"backtest"` Block

```json
{
  "metrics": {
    "sharpe": 1.42,
    "pnl": 0.34,
    "max_drawdown": -0.08
  },
  "signal": {
    "index": [...],
    "values": [...]
  },
  "strategy_returns": {
    "index": [...],
    "values": [...]
  },
  "cumulative_returns": {
    "index": [...],
    "values": [...]
  }
}
```

Matches your Step 4 serializer.

---

## 4. `"dataset"` Block

```json
{
  "id": "btc-usdt-1d-v0.1",
  "hash": "sha256....",
  "symbol": "BTC-USDT",
  "timeframe": "1D",
  "range": "2018-01-01 to 2024-01-01"
}
```

---

## 5. `"zk"` Block

```json
{
  "proof_system": "risc0",
  "program_id": "hex-program-id",
  "proof": "base64-encoded-receipt",
  "public_journal": {
    "dataset_hash": "...",
    "signal_hash": "...",
    "strategy_returns_hash": "...",
    "cumulative_returns_hash": "...",
    "metrics": { ... }
  }
}
```

All RISC Zero outputs stored here.

---

## 6. `"metadata"` Block

```json
{
  "created_at": "2025-01-01T00:00:00Z",
  "engine_version": "0.1",
  "esl_version": "0.1",
  "dataset_version": "0.1"
}
```

---

## 7. Versioning Rules

* Any changes to schema → new artifact version (0.3+)
* ZK field changes → new version
* Dataset changes → increment dataset_version

---

This schema is final for EverythingSignal v0.2.