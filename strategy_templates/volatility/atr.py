"""ATR-based Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class ATRBreakout(Strategy):
    """ATR Breakout Strategy"""
    def __init__(self, params: Dict):
        super().__init__("ATRBreakout", params)
        self.period = params.get("period", 14)
        self.multiplier = params.get("multiplier", 2.0)
        self.rules = [{"type": "entry_long", "condition": "price moves up > ATR * multiplier"},
                     {"type": "entry_short", "condition": "price moves down > ATR * multiplier"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            close = df.get("close", df.get("mid_price"))
            tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            price_change = close.diff()
            signals[price_change > self.multiplier * atr] = 1
            signals[price_change < -self.multiplier * atr] = -1
        return signals

class ATRChannelBreak(Strategy):
    """ATR Channel Breakout"""
    def __init__(self, params: Dict):
        super().__init__("ATRChannelBreak", params)
        self.period = params.get("period", 14)
        self.multiplier = params.get("multiplier", 2.0)
        self.rules = [{"type": "entry_long", "condition": "close > upper ATR channel"},
                     {"type": "entry_short", "condition": "close < lower ATR channel"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            close = df.get("close", df.get("mid_price"))
            tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            sma = close.rolling(self.period).mean()
            upper = sma + self.multiplier * atr
            lower = sma - self.multiplier * atr
            signals[close > upper] = 1
            signals[close < lower] = -1
        return signals

class ATRTrailing(Strategy):
    """ATR Trailing Stop"""
    def __init__(self, params: Dict):
        super().__init__("ATRTrailing", params)
        self.period = params.get("period", 14)
        self.multiplier = params.get("multiplier", 3.0)
        self.rules = [{"type": "entry_long", "condition": "price crosses above ATR trailing stop"},
                     {"type": "entry_short", "condition": "price crosses below ATR trailing stop"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            close = df.get("close", df.get("mid_price"))
            tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
            atr = tr.rolling(self.period).mean()
            stop = close - self.multiplier * atr
            signals[(close > stop.shift(1)) & (close.shift(1) <= stop.shift(2))] = 1
            signals[(close < stop.shift(1)) & (close.shift(1) >= stop.shift(2))] = -1
        return signals
