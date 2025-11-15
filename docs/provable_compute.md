# 🔐 EverythingSignal Provable Compute Architecture (v0.1)

This document defines the design for running model evaluation + backtesting inside a **ZK-verifiable environment**, using **RISC Zero**.

---

## 1. Why ZK?

Marketplace users must be able to trust that:

- backtest results are NOT faked
- models are evaluated on a known dataset
- metrics match actual engine output

ZK allows:

✔ Creator hides model  
✔ Buyer sees metrics + proof  
✔ Verifier checks proof without rerunning engine  

---

## 2. Architecture Overview

```
     +--------------------+
     |   Python Engine    |
     |  (reference impl)  |
     +----------+---------+
                |
        (translated spec)
                |
     +----------v----------+
     |   RISC Zero Guest   |   <--- Rust implementation
     |  ESL + Backtester   |
     +----------+----------+
                |
            Produces
                |
 +-----------------------------+
 |   Proof (receipt)          |
 |   Public Journal           |
 +-----------------------------+
```

The Python engine defines **the spec**, and the Rust RISC Zero guest must match it exactly.

---

## 3. Public vs Private Inputs

### 🔓 Public Inputs
Visible to verifier:

| Field                    | Description                                  |
|-------------------------|----------------------------------------------|
| dataset_hash            | SHA-256 hash of canonical dataset            |
| signal_hash             | hash of computed signal                      |
| strategy_returns_hash   | hash of per-day returns                      |
| cumulative_returns_hash | hash of cumulative returns                   |
| metrics                 | (sharpe, pnl, drawdown, turnover, etc.)      |

### 🔒 Private Inputs
Hidden inside the ZK execution:

| Field           | Description                 |
|-----------------|-----------------------------|
| model JSON      | ESL operator tree           |
| dataset values  | the actual price series     |

---

## 4. What the ZK Program Proves

The RISC Zero guest code must implement:

1. ESL evaluation  
2. Backtester logic  
3. Metric calculation  
4. Hashing of:
   - signal
   - strategy_returns
   - cumulative_returns  
5. Output metrics to the public journal  

The proof guarantees:

```
"These metrics and hashes are correct for this model and this dataset."
```

---

## 5. Public Journal Format (RISC Zero)

Example structure:

```json
{
  "dataset_hash": "abcd1234...",
  "signal_hash": "f00baa...",
  "strategy_returns_hash": "...",
  "cumulative_returns_hash": "...",
  "metrics": {
    "sharpe": 1.42,
    "pnl": 0.34,
    "max_drawdown": -0.08
  }
}
```

This journal is included in the EverythingSignal Artifact v0.2.

---

## 6. Proof Output

RISC Zero produces:

* **receipt** (binary proof)
* **journal bytes** (public data)

These are stored in Walrus.

---

## 7. Verifier Workflow

Anyone can verify:

```
receipt.verify(program_id, journal)
```

If valid, the model performance is proven.

---

## 8. Why RISC Zero?

* Native Rust execution
* Can use full loops + arrays
* Perfect for time-series DSL
* You already used it (zkOTP)
* Great for hackathon demos

---

## 9. Future Versions

v0.2 may expand to multi-asset, 1H data, or per-minute.