"""Time-based Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class AsianRangeBreakout(Strategy):
    """Asian Session Range Breakout"""
    def __init__(self, params: Dict):
        super().__init__("AsianRangeBreakout", params)
        self.rules = [{"type": "entry_long", "condition": "breakout of Asian range bullish"}, {"type": "entry_short", "condition": "breakout of Asian range bearish"}]
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

class LondonOpenBreakout(Strategy):
    """London Open Breakout"""
    def __init__(self, params: Dict):
        super().__init__("LondonOpenBreakout", params)
        self.rules = [{"type": "entry_long", "condition": "trade London open volatility bullish"}, {"type": "entry_short", "condition": "trade London open volatility bearish"}]
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

class NYOpenStrategy(Strategy):
    """New York Open Strategy"""
    def __init__(self, params: Dict):
        super().__init__("NYOpenStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "NY open volatility bullish"}, {"type": "entry_short", "condition": "NY open volatility bearish"}]
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

class LondonNYOverlap(Strategy):
    """London-NY Overlap"""
    def __init__(self, params: Dict):
        super().__init__("LondonNYOverlap", params)
        self.rules = [{"type": "entry_long", "condition": "trade session overlap bullish"}, {"type": "entry_short", "condition": "trade session overlap bearish"}]
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

class SessionClose(Strategy):
    """Session Close Strategy"""
    def __init__(self, params: Dict):
        super().__init__("SessionClose", params)
        self.rules = [{"type": "entry_long", "condition": "trade before session close bullish"}, {"type": "entry_short", "condition": "trade before session close bearish"}]
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

