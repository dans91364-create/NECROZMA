"""Multi-pair Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class LeadLagStrategy(Strategy):
    """Lead-Lag Relationship"""
    def __init__(self, params: Dict):
        super().__init__("LeadLagStrategy", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "one pair leads another bullish signal"}, {"type": "entry_short", "condition": "one pair leads another bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class StatisticalArbitrage(Strategy):
    """Statistical Arbitrage"""
    def __init__(self, params: Dict):
        super().__init__("StatisticalArbitrage", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "mean reversion of spread bullish signal"}, {"type": "entry_short", "condition": "mean reversion of spread bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class SpreadTrading(Strategy):
    """Spread Trading"""
    def __init__(self, params: Dict):
        super().__init__("SpreadTrading", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "trade pair spread bullish signal"}, {"type": "entry_short", "condition": "trade pair spread bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

