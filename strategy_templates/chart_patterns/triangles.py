"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class AscendingTriangle(Strategy):
    """Ascending Triangle"""
    def __init__(self, params: Dict):
        super().__init__("AscendingTriangle", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "flat top, rising lows confirmed"}, {"type": "entry_short", "condition": "flat top, rising lows reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class DescendingTriangle(Strategy):
    """Descending Triangle"""
    def __init__(self, params: Dict):
        super().__init__("DescendingTriangle", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "flat bottom, falling highs confirmed"}, {"type": "entry_short", "condition": "flat bottom, falling highs reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class SymmetricalTriangle(Strategy):
    """Symmetrical Triangle"""
    def __init__(self, params: Dict):
        super().__init__("SymmetricalTriangle", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "converging highs and lows confirmed"}, {"type": "entry_short", "condition": "converging highs and lows reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

