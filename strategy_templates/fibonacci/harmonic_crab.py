"""Fibonacci and Harmonic Patterns"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy

class CrabPattern(Strategy):
    """Crab Harmonic Pattern"""
    def __init__(self, params: Dict):
        super().__init__("CrabPattern", params)
        self.lookback = params.get("lookback", 50)
        self.fib_level = params.get("fib_level", "XABCD Crab")
        self.rules = [{"type": "entry_long", "condition": "price retraces to XABCD Crab level"}, {"type": "entry_short", "condition": "price extends beyond XABCD Crab"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            fib_level_price = swing_low + (swing_high - swing_low) * self.fib_level
            # Buy when price reaches fib level from above, sell from below
            signals[(price <= fib_level_price) & (price.shift(1) > fib_level_price.shift(1))], signals[(price >= fib_level_price) & (price.shift(1) < fib_level_price.shift(1))] = 1, -1
        return signals

