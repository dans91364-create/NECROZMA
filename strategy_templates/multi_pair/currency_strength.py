"""Multi-pair Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class CurrencyStrength(Strategy):
    """Currency Strength Index"""
    def __init__(self, params: Dict):
        super().__init__("CurrencyStrength", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "relative currency strength bullish signal"}, {"type": "entry_short", "condition": "relative currency strength bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class USDStrengthIndex(Strategy):
    """USD Strength Index"""
    def __init__(self, params: Dict):
        super().__init__("USDStrengthIndex", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "USD vs basket bullish signal"}, {"type": "entry_short", "condition": "USD vs basket bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class DXYFollower(Strategy):
    """DXY Follower"""
    def __init__(self, params: Dict):
        super().__init__("DXYFollower", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "follow dollar index bullish signal"}, {"type": "entry_short", "condition": "follow dollar index bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class G10Momentum(Strategy):
    """G10 Momentum"""
    def __init__(self, params: Dict):
        super().__init__("G10Momentum", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "G10 currency momentum bullish signal"}, {"type": "entry_short", "condition": "G10 currency momentum bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

