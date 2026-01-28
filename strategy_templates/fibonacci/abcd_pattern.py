"""Fibonacci and Harmonic Patterns"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy

class ABCDPattern(Strategy):
    """ABCD Pattern"""
    def __init__(self, params: Dict):
        super().__init__("ABCDPattern", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", "Simple ABCD")
        self.rules = [{"type": "entry_long", "condition": "price retraces to Simple ABCD level"}, {"type": "entry_short", "condition": "price extends beyond Simple ABCD"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

class ThreeDrivesPattern(Strategy):
    """Three Drives Pattern"""
    def __init__(self, params: Dict):
        super().__init__("ThreeDrivesPattern", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", "Three drives")
        self.rules = [{"type": "entry_long", "condition": "price retraces to Three drives level"}, {"type": "entry_short", "condition": "price extends beyond Three drives"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

