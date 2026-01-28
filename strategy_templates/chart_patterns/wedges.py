"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class RisingWedge(Strategy):
    """Rising Wedge"""
    def __init__(self, params: Dict):
        super().__init__("RisingWedge", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "rising highs and lows, converging confirmed"}, {"type": "entry_short", "condition": "rising highs and lows, converging reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class FallingWedge(Strategy):
    """Falling Wedge"""
    def __init__(self, params: Dict):
        super().__init__("FallingWedge", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "falling highs and lows, converging confirmed"}, {"type": "entry_short", "condition": "falling highs and lows, converging reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

