"""Fibonacci and Harmonic Patterns"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy

class FibRetracement382(Strategy):
    """38.2% Fibonacci Retracement"""
    def __init__(self, params: Dict):
        super().__init__("FibRetracement382", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", 0.382)
        self.rules = [{"type": "entry_long", "condition": "price retraces to 0.382 level"}, {"type": "entry_short", "condition": "price extends beyond 0.382"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

class FibRetracement50(Strategy):
    """50% Fibonacci Retracement"""
    def __init__(self, params: Dict):
        super().__init__("FibRetracement50", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", 0.5)
        self.rules = [{"type": "entry_long", "condition": "price retraces to 0.5 level"}, {"type": "entry_short", "condition": "price extends beyond 0.5"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

class FibRetracement618(Strategy):
    """61.8% Fibonacci Retracement"""
    def __init__(self, params: Dict):
        super().__init__("FibRetracement618", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", 0.618)
        self.rules = [{"type": "entry_long", "condition": "price retraces to 0.618 level"}, {"type": "entry_short", "condition": "price extends beyond 0.618"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

