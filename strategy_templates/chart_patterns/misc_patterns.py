"""Chart Pattern Recognition"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class RoundingBottom(Strategy):
    """Rounding Bottom"""
    def __init__(self, params: Dict):
        super().__init__("RoundingBottom", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "gradual U-shaped bottom confirmed"}, {"type": "entry_short", "condition": "gradual U-shaped bottom reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class RoundingTop(Strategy):
    """Rounding Top"""
    def __init__(self, params: Dict):
        super().__init__("RoundingTop", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "gradual inverted U-shaped top confirmed"}, {"type": "entry_short", "condition": "gradual inverted U-shaped top reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class DiamondPattern(Strategy):
    """Diamond Pattern"""
    def __init__(self, params: Dict):
        super().__init__("DiamondPattern", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "widening then narrowing range confirmed"}, {"type": "entry_short", "condition": "widening then narrowing range reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class BroadeningFormation(Strategy):
    """Broadening Formation"""
    def __init__(self, params: Dict):
        super().__init__("BroadeningFormation", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "expanding highs and lows confirmed"}, {"type": "entry_short", "condition": "expanding highs and lows reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

class BumpAndRun(Strategy):
    """Bump and Run"""
    def __init__(self, params: Dict):
        super().__init__("BumpAndRun", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "parabolic rise then reversal confirmed"}, {"type": "entry_short", "condition": "parabolic rise then reversal reversed"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            high_roll, low_roll = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Simplified pattern: breakout above high or below low
            signals[price > high_roll.shift(1)], signals[price < low_roll.shift(1)] = 1, -1
        return signals

