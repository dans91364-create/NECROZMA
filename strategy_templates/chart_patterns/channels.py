"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class Rectangle(Strategy):
    """Rectangle"""
    def __init__(self, params: Dict):
        super().__init__("Rectangle", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "horizontal support and resistance confirmed"}, {"type": "entry_short", "condition": "horizontal support and resistance reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class ChannelUp(Strategy):
    """Channel Up"""
    def __init__(self, params: Dict):
        super().__init__("ChannelUp", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "rising parallel lines confirmed"}, {"type": "entry_short", "condition": "rising parallel lines reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class ChannelDown(Strategy):
    """Channel Down"""
    def __init__(self, params: Dict):
        super().__init__("ChannelDown", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "falling parallel lines confirmed"}, {"type": "entry_short", "condition": "falling parallel lines reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

