# engine/executor.py

from __future__ import annotations

from typing import Any, Mapping, Sequence

import pandas as pd

from .operators import OPERATOR_REGISTRY, Series


class ESLExecutionError(Exception):
    """Generic error while executing an ESL expression."""


def _resolve_leaf(node: Any, data: pd.DataFrame) -> Any:
    """
    Resolve a leaf node:
    - string matching a column name -> Series
    - numeric -> numeric (int/float)
    - Series -> Series
    """
    if isinstance(node, str):
        if node in data:
            return data[node]
        raise ESLExecutionError(f"Unknown field reference: {node}")
    if isinstance(node, (int, float)):
        return node
    if isinstance(node, pd.Series):
        return node
    raise ESLExecutionError(f"Unsupported leaf type: {type(node)} ({node})")


def eval_node(node: Any, data: pd.DataFrame) -> Series:
    """
    Evaluate a JSON operator tree node against a price dataframe.

    Expected node formats:

    - Operator:
        {
          "op": "SMA",
          "args": ["close", 10]
        }

    - Field:
        "close"

    - Constant:
        5, 10.0, etc.

    Returns:
        pd.Series with the same index as `data`.
    """
    # Operator node
    if isinstance(node, Mapping):
        if "op" not in node:
            raise ESLExecutionError(f"Missing 'op' in node: {node}")
        op_name_raw = node["op"]
        if not isinstance(op_name_raw, str):
            raise ESLExecutionError(f"'op' must be a string: {node}")

        op_name = op_name_raw.upper()
        if op_name not in OPERATOR_REGISTRY:
            raise ESLExecutionError(f"Unknown operator: {op_name}")

        fn = OPERATOR_REGISTRY[op_name]

        args_nodes = node.get("args", [])
        if not isinstance(args_nodes, Sequence):
            raise ESLExecutionError(f"'args' must be a list/sequence: {node}")

        evaluated_args: list[Any] = []
        for arg in args_nodes:
            if isinstance(arg, Mapping):
                # Nested operator node
                evaluated_args.append(eval_node(arg, data))
            elif isinstance(arg, (dict, list)):
                # Defensive: any dict is treated as operator node, any list is illegal for now
                if isinstance(arg, list):
                    raise ESLExecutionError(
                        f"List args are not supported directly in ESL: {arg}"
                    )
            else:
                # Could be field, number, Series
                evaluated_args.append(_resolve_leaf(arg, data))

        try:
            result = fn(*evaluated_args)
        except Exception as e:
            raise ESLExecutionError(
                f"Error while executing operator '{op_name}' "
                f"with args {evaluated_args}: {e}"
            ) from e

        if not isinstance(result, pd.Series):
            # Many ops will naturally return Series, but enforce it for Step 2
            # If scalar appears, broadcast to series matching the data index
            if isinstance(result, (int, float)):
                result = pd.Series(result, index=data.index)
            else:
                raise ESLExecutionError(
                    f"Operator '{op_name}' did not return a Series: {type(result)}"
                )

        return result

    # Leaf node (field or constant)
    return _resolve_leaf(node, data)  # type: ignore[return-value]


def evaluate_expression_tree(tree: Mapping[str, Any], data: pd.DataFrame) -> Series:
    """
    Public API for Step 2.

    Args:
        tree: JSON operator tree (dict), canonical ESL representation.
        data: pd.DataFrame with columns: open, high, low, close, volume, ...

    Returns:
        pd.Series with DatetimeIndex (matching `data.index`).
    """
    result = eval_node(tree, data)
    if not isinstance(result, pd.Series):
        raise ESLExecutionError(
            f"Top-level evaluation did not return a Series: {type(result)}"
        )
    # Ensure index alignment with input data
    if not result.index.equals(data.index):
        result = result.reindex(data.index)
    return result
