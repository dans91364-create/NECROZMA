"""Time-based Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class EndOfMonth(Strategy):
    """End of Month Effect"""
    def __init__(self, params: Dict):
        super().__init__("EndOfMonth", params)
        self.rules = [{"type": "entry_long", "condition": "month-end rebalancing bullish"}, {"type": "entry_short", "condition": "month-end rebalancing bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price action as proxy for time patterns
        if hasattr(df.index, 'hour'):
            hour = pd.Series(df.index.hour, index=df.index)
            # Trade during active hours (8-16 UTC)
            active = (hour >= 8) & (hour < 16)
            signals[active & (price > price.shift(1))], signals[active & (price < price.shift(1))] = 1, -1
        else:
            signals[price > price.rolling(5).mean()], signals[price < price.rolling(5).mean()] = 1, -1
        return signals

class TurnOfMonth(Strategy):
    """Turn of Month"""
    def __init__(self, params: Dict):
        super().__init__("TurnOfMonth", params)
        self.rules = [{"type": "entry_long", "condition": "last/first days of month bullish"}, {"type": "entry_short", "condition": "last/first days of month bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price action as proxy for time patterns
        if hasattr(df.index, 'hour'):
            hour = pd.Series(df.index.hour, index=df.index)
            # Trade during active hours (8-16 UTC)
            active = (hour >= 8) & (hour < 16)
            signals[active & (price > price.shift(1))], signals[active & (price < price.shift(1))] = 1, -1
        else:
            signals[price > price.rolling(5).mean()], signals[price < price.rolling(5).mean()] = 1, -1
        return signals

class WeeklyOpenGap(Strategy):
    """Weekly Open Gap"""
    def __init__(self, params: Dict):
        super().__init__("WeeklyOpenGap", params)
        self.rules = [{"type": "entry_long", "condition": "Sunday/Monday gap trading bullish"}, {"type": "entry_short", "condition": "Sunday/Monday gap trading bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price action as proxy for time patterns
        if hasattr(df.index, 'hour'):
            hour = pd.Series(df.index.hour, index=df.index)
            # Trade during active hours (8-16 UTC)
            active = (hour >= 8) & (hour < 16)
            signals[active & (price > price.shift(1))], signals[active & (price < price.shift(1))] = 1, -1
        else:
            signals[price > price.rolling(5).mean()], signals[price < price.rolling(5).mean()] = 1, -1
        return signals

