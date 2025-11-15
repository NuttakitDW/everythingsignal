# 📄 **EverythingSignal Language (ESL) — Minimal Specification (v0.1)**

*A lightweight, original expression language for quantitative models.*

---

## **1. Overview**

The EverythingSignal Language (ESL) is a simple and transparent expression language designed to define quantitative trading signals.
The language focuses on clarity, mathematical correctness, and extensibility while remaining minimal and easy to learn.

---

## **2. Supported Data Fields**

ESL operates on universal market data fields commonly available in any financial dataset:

* `open`
* `high`
* `low`
* `close`
* `volume`

These fields form the foundation of most time-series analysis and technical indicators.

---

## **3. Core Mathematical Operators**

All operators use a functional format:

```
OPERATION(arg1, arg2, ...)
```

### Arithmetic

* `ADD(x, y)` — element-wise addition
* `SUB(x, y)` — element-wise subtraction
* `MUL(x, y)` — element-wise multiplication
* `DIV(x, y)` — element-wise division

### Transformations

* `ABS(x)` — absolute value
* `LOG(x)` — natural logarithm

---

## **4. Time-Series Operators**

These operators enable historical and rolling-window calculations with clean and intuitive names.

### Moving Averages

* `SMA(x, n)`
  Simple moving average over the last `n` periods.

* `EMA(x, n)`
  Exponential moving average with period `n`.

### Lagged Values

* `LAG(x, n)`
  Value of `x` shifted backward by `n` periods.

### Change & Returns

* `DIFF(x, n)`
  Difference between `x` and its value `n` periods ago.

* `RETURN(x, n)`
  Percentage change from `n` periods ago:
  `(x / LAG(x, n)) - 1`.

### Normalization

* `NORMALIZE(x)`
  Standardize `x` to mean 0 and variance 1.

### Rolling Statistics

* `ROLLING_STD(x, n)`
  Rolling standard deviation over `n` periods.

* `ROLLING_MEAN(x, n)`
  Rolling mean over `n` periods (alias of SMA).

---

## **5. Expression Format (Text)**

An ESL expression consists of operators and data fields combined into a single line:

Example:

```
SMA(close, 10) - SMA(close, 30)
```

Another example:

```
NORMALIZE( RETURN(close, 5) ) * volume
```

---

## **6. JSON Operator Tree Format**

Models can also be expressed as JSON for structured processing.

Example:

```json
{
  "op": "SUB",
  "args": [
    { "op": "SMA", "args": ["close", 10] },
    { "op": "SMA", "args": ["close", 30] }
  ]
}
```

Example with nested operations:

```json
{
  "op": "MUL",
  "args": [
    { "op": "NORMALIZE", "args": [
      { "op": "RETURN", "args": ["close", 5] }
    ]},
    "volume"
  ]
}
```

---

## **7. Minimal Grammar (BNF)**

```
EXPR        ::= FUNCTION | FIELD | NUMBER | OPERATION
FIELD       ::= "open" | "high" | "low" | "close" | "volume"
FUNCTION    ::= IDENT "(" ARGS ")"
ARGS        ::= EXPR | EXPR "," ARGS
IDENT       ::= LETTER (LETTER | DIGIT | "_")*
```

---

## **8. Example Models**

### Example 1 — Text

```
SMA(close, 20) - SMA(close, 50)
```

### Example 2 — JSON

```json
{
  "op": "SUB",
  "args": [
    { "op": "EMA", "args": ["close", 20] },
    { "op": "EMA", "args": ["close", 50] }
  ]
}
```

### Example 3 — Composite

```
NORMALIZE( DIFF(close, 5) ) * NORMALIZE(volume)
```

---

## **9. Safety & Originality Statement**

The EverythingSignal Language (ESL):

* Uses fully original operator names and syntax
* Is not derived from any existing proprietary expression language
* Is built from first principles using universal mathematical and statistical concepts
* Is safe for open-source and commercial use