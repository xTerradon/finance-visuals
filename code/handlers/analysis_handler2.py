import pandas as pd
import numpy as np
from itertools import product

def annotate_previous_movement(data: pd.DataFrame, history_len: int) -> pd.DataFrame:
    """Annotates the dataframe with previous movement history."""
    close_diff = np.sign(data["close"].diff().fillna(0))
    prev_movements = np.column_stack([np.roll(close_diff, i) for i in range(1, history_len + 1)])
    prev_movements[:history_len, :] = np.nan  # Ensure no invalid shifts

    prev_df = pd.DataFrame(prev_movements, columns=[f"prev_{i}" for i in range(1, history_len + 1)], index=data.index)
    return pd.concat([data, prev_df], axis=1).dropna().astype(int)

def annotate_return(data: pd.DataFrame, future_len: int) -> pd.DataFrame:
    """Annotates the dataframe with future returns."""
    close_arr = data["close"].values
    returns = np.column_stack([(np.roll(close_arr, -i) - close_arr) / close_arr for i in range(1, future_len + 1)])
    return_df = pd.DataFrame(returns, columns=[f"return_{i}" for i in range(1, future_len + 1)], index=data.index)
    return pd.concat([data, return_df], axis=1)

def get_stats_from_previous_movement(data: pd.DataFrame, history_len: int, return_len: int) -> pd.DataFrame:
    """Computes statistics for each pattern of previous movements."""
    data = annotate_previous_movement(data, history_len)
    data = annotate_return(data, return_len)

    # Group by previous movement pattern and compute mean returns
    group_cols = [f"prev_{i}" for i in range(1, history_len + 1)]
    stats = data.groupby(group_cols).agg(
        count=("close", "count"),
        **{f"return_{i}": (f"return_{i}", "mean") for i in range(1, return_len + 1)}
    ).reset_index()

    # Convert numerical patterns to list representation
    stats["pattern"] = stats[group_cols].values.tolist()
    stats = stats.drop(columns=group_cols).sort_values("count", ascending=False)

    return stats
