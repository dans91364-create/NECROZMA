"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class DoubleTop(Strategy):
    """Double Top"""
    def __init__(self, params: Dict):
        super().__init__("DoubleTop", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "two peaks at resistance confirmed"}, {"type": "entry_short", "condition": "two peaks at resistance reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class DoubleBottom(Strategy):
    """Double Bottom"""
    def __init__(self, params: Dict):
        super().__init__("DoubleBottom", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "two troughs at support confirmed"}, {"type": "entry_short", "condition": "two troughs at support reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class TripleTop(Strategy):
    """Triple Top"""
    def __init__(self, params: Dict):
        super().__init__("TripleTop", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "three peaks at resistance confirmed"}, {"type": "entry_short", "condition": "three peaks at resistance reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class TripleBottom(Strategy):
    """Triple Bottom"""
    def __init__(self, params: Dict):
        super().__init__("TripleBottom", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "three troughs at support confirmed"}, {"type": "entry_short", "condition": "three troughs at support reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

