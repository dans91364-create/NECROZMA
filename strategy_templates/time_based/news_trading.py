"""Time-based Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class NFPStrategy(Strategy):
    """Non-Farm Payrolls"""
    def __init__(self, params: Dict):
        super().__init__("NFPStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "NFP release volatility bullish"}, {"type": "entry_short", "condition": "NFP release volatility bearish"}]
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

class FOMCStrategy(Strategy):
    """FOMC Meeting"""
    def __init__(self, params: Dict):
        super().__init__("FOMCStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "Federal Reserve meeting bullish"}, {"type": "entry_short", "condition": "Federal Reserve meeting bearish"}]
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

class ECBStrategy(Strategy):
    """ECB Meeting"""
    def __init__(self, params: Dict):
        super().__init__("ECBStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "European Central Bank bullish"}, {"type": "entry_short", "condition": "European Central Bank bearish"}]
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

