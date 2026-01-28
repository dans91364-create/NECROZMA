"""Time-based Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class DayOfWeekEffect(Strategy):
    """Day of Week Anomaly"""
    def __init__(self, params: Dict):
        super().__init__("DayOfWeekEffect", params)
        self.rules = [{"type": "entry_long", "condition": "trade based on weekday patterns bullish"}, {"type": "entry_short", "condition": "trade based on weekday patterns bearish"}]
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

class MondayReversal(Strategy):
    """Monday Reversal"""
    def __init__(self, params: Dict):
        super().__init__("MondayReversal", params)
        self.rules = [{"type": "entry_long", "condition": "Monday tendency reversal bullish"}, {"type": "entry_short", "condition": "Monday tendency reversal bearish"}]
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

class FridayClose(Strategy):
    """Friday Close Effect"""
    def __init__(self, params: Dict):
        super().__init__("FridayClose", params)
        self.rules = [{"type": "entry_long", "condition": "Friday profit-taking bullish"}, {"type": "entry_short", "condition": "Friday profit-taking bearish"}]
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

