"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class BullFlag(Strategy):
    """Bull Flag"""
    def __init__(self, params: Dict):
        super().__init__("BullFlag", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "brief downward consolidation in uptrend confirmed"}, {"type": "entry_short", "condition": "brief downward consolidation in uptrend reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class BearFlag(Strategy):
    """Bear Flag"""
    def __init__(self, params: Dict):
        super().__init__("BearFlag", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "brief upward consolidation in downtrend confirmed"}, {"type": "entry_short", "condition": "brief upward consolidation in downtrend reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class BullPennant(Strategy):
    """Bull Pennant"""
    def __init__(self, params: Dict):
        super().__init__("BullPennant", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "small symmetrical triangle in uptrend confirmed"}, {"type": "entry_short", "condition": "small symmetrical triangle in uptrend reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class BearPennant(Strategy):
    """Bear Pennant"""
    def __init__(self, params: Dict):
        super().__init__("BearPennant", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "small symmetrical triangle in downtrend confirmed"}, {"type": "entry_short", "condition": "small symmetrical triangle in downtrend reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

