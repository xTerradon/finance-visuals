import pandas as pd
import os

def get_available_symbols():
    available_files = os.listdir("../kraken_data")
    available_symbols = sorted(list(set([file.split("_")[0] for file in available_files])))
    return available_symbols

def get_available_timeframes():
    available_files = os.listdir("../kraken_data")
    possible_timeframes = []
    for file in available_files:
        try:
            possible_timeframes.append(int(file.split("_")[1].split(".")[0]))
        except:
            print(f"Could not extract timeframe from file {file}")
    available_timeframes = sorted(list(set(possible_timeframes)))
    return available_timeframes

def get_data(symbol_name: str, timeframe: str):
    try:
        data = pd.read_csv(f"../kraken_data/{symbol_name}_{timeframe}.csv", names=["timestamp", "open", "high", "low", "close", "volume", "count"])
        data["time"] = pd.to_datetime(data["timestamp"], unit="s")
    except FileNotFoundError:
        print(f"Could not find file {symbol_name}_{timeframe}.csv")
        return None

    return data