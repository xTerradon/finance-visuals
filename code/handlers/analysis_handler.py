import pandas as pd
import numpy as np
from itertools import product

def annotate_previous_movement(data: pd.DataFrame, history_len: int) -> pd.DataFrame:
    data[f"prev_1"] = (((data["close"].shift(1) < data["close"]).astype(int)) * 2 ) -1
    for i in range(2, history_len + 1):
        data[f"prev_{i}"] = data[f"prev_{i - 1}"].shift(1)
    data.dropna(inplace=True)
    for i in range(1, history_len + 1):
        data[f"prev_{i}"] = data[f"prev_{i}"].astype(int)
    return data

def annotate_return(data: pd.DataFrame, future_len: int) -> pd.DataFrame:
    for i in range(1, future_len + 1):
        data[f"return_{i}"] = (data["close"].shift(-i) - data["close"]) / data["close"]
    
    return data

def get_stats_from_previous_movement(data_input: pd.DataFrame, history_len: int, return_len: int) -> pd.DataFrame:
    # Work on a copy of the data
    data = data_input.copy()
    data = annotate_previous_movement(data, history_len)
    data = annotate_return(data, return_len)

    # Define return column names and force them to be float
    return_cols = [f"return_{i}" for i in range(1, return_len + 1)]
    for col in return_cols:
        data[col] = data[col].astype(float)

    n = len(data)

    # Precompute boolean masks for each "prev_i" column for values -1 and 1
    precomputed_masks = {}
    for i in range(history_len):
        col = f"prev_{i+1}"
        col_arr = data[col].to_numpy()
        precomputed_masks[(col, -1)] = (col_arr == -1)
        precomputed_masks[(col, 1)] = (col_arr == 1)

    # Preconvert return columns to numpy arrays
    ret_vals = {col: data[col].to_numpy() for col in return_cols}

    # Get the list of movement patterns
    patterns = generate_possible_movement_patterns(history_len)
    stats = []
    
    for pattern in patterns:
        # Convert pattern to a string list for display
        pattern_str = tuple([p for p in pattern])
        # Start with a full True mask (all rows)
        mask = np.ones(n, dtype=bool)
        for i, p in enumerate(pattern):
            if p != 0:
                col = f"prev_{i+1}"
                mask &= precomputed_masks[(col, p)]
        
        count = mask.sum()
        # Use nonzero indices to compute means more directly
        indices = np.nonzero(mask)[0]
        means = []
        for col in return_cols:
            if count > 0:
                # Use np.nanmean to avoid propagating any NaNs in the array
                means.append(np.nanmean(ret_vals[col][indices]))
            else:
                means.append(np.nan)
        stats.append([pattern_str, count] + means)
    
    # Build the result DataFrame and reset the index after sorting
    df = pd.DataFrame(stats, columns=["pattern", "count"] + return_cols)
    df = df.sort_values("count", ascending=False).reset_index(drop=True)
    return df




def generate_possible_movement_patterns(n: int):
    indices = np.indices([3] * n).reshape(n, -1).T
    
    mapping = np.array([-1, 0, 1])
    return mapping[indices]